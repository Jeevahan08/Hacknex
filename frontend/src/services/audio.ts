/**
 * AudioStreamService — captures microphone audio and sends PCM chunks to the WebSocket server.
 *
 * ARCHITECTURE:
 *   Microphone → ScriptProcessor → PCM Int16 → Base64 → WebSocket → Backend STT
 *
 * The browser's built-in SpeechRecognition API is used ONLY for local volume/activity
 * detection, NOT for transcription. All transcription goes through the Sarvam Saaras v4
 * STT via the backend WebSocket.
 *
 * CRITICAL FIX: Previously, SpeechRecognition.onresult was firing English transcripts
 * via transcript.stream which bypassed the translation pipeline (source text was being
 * used as the translation output). This is now disabled — all text goes through the
 * proper STT → Commit → Translate pipeline on the backend.
 */
export class AudioStreamService {
  private mediaStream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private processor: ScriptProcessorNode | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private onAudioChunkCallback: ((base64Chunk: string) => void) | null = null;
  private onVolumeChangeCallback: ((volume: number) => void) | null = null;
  private isCapturing: boolean = false;
  private chunkCount: number = 0;

  async startCapture(
    sourceLanguage: string,
    onChunk: (base64Chunk: string) => void,
    onVolume?: (volume: number) => void,
    // onTranscript is intentionally ignored — transcription happens server-side via STT API
    _onTranscript?: (transcript: string, isFinal: boolean) => void
  ): Promise<boolean> {
    try {
      this.onAudioChunkCallback = onChunk;
      this.onVolumeChangeCallback = onVolume || null;
      this.chunkCount = 0;

      // 1. Acquire microphone stream at 16kHz for Sarvam STT compatibility
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      // 2. Initialize AudioContext at 16kHz
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      this.audioContext = new AudioCtx({ sampleRate: 16000 });
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }

      this.source = this.audioContext.createMediaStreamSource(this.mediaStream);
      // 4096 samples @ 16kHz = 256ms per callback — good balance of latency vs overhead
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

      this.processor.onaudioprocess = (e) => {
        if (!this.isCapturing) return;

        const inputData = e.inputBuffer.getChannelData(0);

        // Compute RMS volume for animated waveform display
        let sum = 0;
        for (let i = 0; i < inputData.length; i++) {
          sum += inputData[i] * inputData[i];
        }
        const rms = Math.sqrt(sum / inputData.length);
        if (this.onVolumeChangeCallback) {
          this.onVolumeChangeCallback(Math.min(1.0, rms * 5.0));
        }

        // Convert Float32 PCM to 16-bit Linear PCM (required by Sarvam STT API)
        const pcm16 = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }

        // Base64-encode the raw PCM bytes for WebSocket transport
        const bytes = new Uint8Array(pcm16.buffer);
        let binary = '';
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
          binary += String.fromCharCode(bytes[i]);
        }
        const base64Chunk = btoa(binary);

        this.chunkCount++;
        if (this.onAudioChunkCallback) {
          this.onAudioChunkCallback(base64Chunk);
        }
      };

      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);

      // NOTE: Browser SpeechRecognition is intentionally NOT used here.
      // Previously it was used and caused the critical bug where English transcripts
      // were sent as transcript.stream messages and appeared as "translations".
      // All speech recognition now goes through the Sarvam Saaras v4 STT API on the backend.

      this.isCapturing = true;
      console.log('[AudioStreamService] Capture started — 16kHz PCM → WebSocket → Sarvam STT');
      return true;
    } catch (err) {
      console.error('[AudioStreamService] Failed to access microphone:', err);
      throw err;
    }
  }

  stopCapture() {
    this.isCapturing = false;
    console.log(`[AudioStreamService] Capture stopped — total chunks sent: ${this.chunkCount}`);

    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.source) {
      this.source.disconnect();
      this.source = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }
    if (this.onVolumeChangeCallback) {
      this.onVolumeChangeCallback(0);
    }
  }

  isActive(): boolean {
    return this.isCapturing;
  }

  getChunkCount(): number {
    return this.chunkCount;
  }
}

export const audioStreamService = new AudioStreamService();
