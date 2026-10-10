import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Download, CheckCircle } from 'lucide-react';
import { apiService } from '../services/api';

interface Term {
  id?: number;
  term: string;
  action: string;
  replacement?: string;
  target_language?: string;
}

export const Glossary: React.FC = () => {
  const [terms, setTerms] = useState<Term[]>([]);
  const [newTerm, setNewTerm] = useState('');
  const [newAction, setNewAction] = useState('preserve');
  const [newReplacement, setNewReplacement] = useState('');
  const [newTargetLang] = useState('ta-IN');
  const [message, setMessage] = useState('');

  const loadGlossary = () => {
    apiService.getGlossary().then((res) => {
      setTerms(res.items || []);
    }).catch(console.error);
  };

  useEffect(() => {
    loadGlossary();
  }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTerm.trim()) return;

    try {
      await apiService.addGlossaryTerm({
        term: newTerm.trim(),
        action: newAction,
        replacement: newAction === 'preferred' ? newReplacement.trim() : undefined,
        target_language: newAction === 'preferred' ? newTargetLang : undefined
      });
      setNewTerm('');
      setNewReplacement('');
      setMessage('Term saved successfully');
      setTimeout(() => setMessage(''), 3000);
      loadGlossary();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id?: number) => {
    if (!id) return;
    try {
      await apiService.deleteGlossaryTerm(id);
      loadGlossary();
    } catch (err) {
      console.error(err);
    }
  };

  const exportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(terms, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", "indiclive_glossary.json");
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-brand-600 bg-brand-50 px-2.5 py-0.5 rounded-full border border-brand-200">
            Entity & Terminology Engine
          </span>
          <h2 className="text-xl font-bold text-slate-900 mt-1">Custom Glossary Manager</h2>
          <p className="text-xs text-slate-500">
            Define terms to strictly preserve across translations (names, places, acronyms) or supply preferred domain translations.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={exportJSON}
            className="flex items-center space-x-1.5 text-xs font-semibold bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 px-3.5 py-2 rounded-xl transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Add Term Form */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center space-x-2">
          <Plus className="w-4 h-4 text-brand-600" />
          <span>Add Custom Term</span>
        </h3>

        <form onSubmit={handleAdd} className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input
            type="text"
            value={newTerm}
            onChange={(e) => setNewTerm(e.target.value)}
            placeholder="Term (e.g. Perundurai, ISRO)"
            className="bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500"
            required
          />

          <select
            value={newAction}
            onChange={(e) => setNewAction(e.target.value)}
            className="bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500 font-medium"
          >
            <option value="preserve">Preserve (Do Not Translate)</option>
            <option value="preferred">Preferred Translation</option>
          </select>

          {newAction === 'preferred' && (
            <input
              type="text"
              value={newReplacement}
              onChange={(e) => setNewReplacement(e.target.value)}
              placeholder="Preferred target translation"
              className="bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500"
              required
            />
          )}

          <button
            type="submit"
            className="bg-brand-600 hover:bg-brand-700 text-white font-semibold px-4 py-2 rounded-xl text-xs transition-colors flex items-center justify-center space-x-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Save Term</span>
          </button>
        </form>

        {message && (
          <p className="text-xs text-emerald-600 font-medium mt-2 flex items-center space-x-1">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>{message}</span>
          </p>
        )}
      </div>

      {/* Glossary Terms Table */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-3 px-4">Term</th>
              <th className="py-3 px-4">Action</th>
              <th className="py-3 px-4">Preferred Translation</th>
              <th className="py-3 px-4">Target Language</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-normal">
            {terms.map((item, idx) => (
              <tr key={item.id || idx} className="hover:bg-slate-50/50">
                <td className="py-3 px-4 font-bold text-slate-900">{item.term}</td>
                <td className="py-3 px-4">
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                      item.action === 'preserve'
                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                        : 'bg-brand-50 text-brand-700 border-brand-200'
                    }`}
                  >
                    {item.action === 'preserve' ? 'Preserve' : 'Preferred'}
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-600">{item.replacement || '—'}</td>
                <td className="py-3 px-4 font-mono text-slate-500">{item.target_language || 'All Targets'}</td>
                <td className="py-3 px-4 text-right">
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="p-1 text-slate-400 hover:text-rose-600 transition-colors"
                    title="Delete term"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
