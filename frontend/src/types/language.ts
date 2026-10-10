export interface Language {
  code: string;
  name: string;
  native_name: string;
  script: string;
  direction: 'ltr' | 'rtl';
  enabled: boolean;
  is_source: boolean;
  is_target: boolean;
}

export const INITIAL_LANGUAGES: Language[] = [
  {
    code: 'en-IN',
    name: 'English',
    native_name: 'English (India)',
    script: 'Latin',
    direction: 'ltr',
    enabled: true,
    is_source: true,
    is_target: true
  },
  {
    code: 'ta-IN',
    name: 'Tamil',
    native_name: 'தமிழ்',
    script: 'Tamil',
    direction: 'ltr',
    enabled: true,
    is_source: true,
    is_target: true
  },
  {
    code: 'hi-IN',
    name: 'Hindi',
    native_name: 'हिन्दी',
    script: 'Devanagari',
    direction: 'ltr',
    enabled: true,
    is_source: true,
    is_target: true
  },
  {
    code: 'ml-IN',
    name: 'Malayalam',
    native_name: 'മലയാളം',
    script: 'Malayalam',
    direction: 'ltr',
    enabled: true,
    is_source: true,
    is_target: true
  },
  {
    code: 'te-IN',
    name: 'Telugu',
    native_name: 'తెలుగు',
    script: 'Telugu',
    direction: 'ltr',
    enabled: true,
    is_source: true,
    is_target: true
  },
  {
    code: 'kn-IN',
    name: 'Kannada',
    native_name: 'ಕನ್ನಡ',
    script: 'Kannada',
    direction: 'ltr',
    enabled: true,
    is_source: true,
    is_target: true
  },
  {
    code: 'mr-IN',
    name: 'Marathi',
    native_name: 'मराठी',
    script: 'Devanagari',
    direction: 'ltr',
    enabled: true,
    is_source: true,
    is_target: true
  }
];
