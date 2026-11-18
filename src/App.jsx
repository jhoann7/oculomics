import React, { useEffect, useState } from 'react';
import { Activity, ArrowUpFromLine, BrainCircuit, CheckCircle2, FileImage, HeartPulse, Info, LockKeyhole, ShieldCheck, Stethoscope, X } from 'lucide-react';
const MAX_BYTES = 10 * 1024 * 1024;
const ENDPOINT = (import.meta.env.VITE_INFERENCE_API_URL || '').replace(/\/$/, '');
const labels = {
  diabetic_retinopathy: 'Retinopatia diabética',
  macular_edema: 'Edema macular',
  hypertensive_retinopathy: 'Retinopatia hipertensiva',
  hemorrhage: 'Hemorragia retiniana',
  vascular_occlusion: 'Oclusão vascular',
  amd: 'Degeneração macular relacionada à idade',
  drusen: 'Drusas',
  retinal_detachment: 'Descolamento de retina',
  increased_cup_disc: 'Escavação papilar aumentada',
  myopic_fundus: 'Fundo miópico',
  scar: 'Cicatriz',
  nevus: 'Nevo retiniano',
  other: 'Outras alterações',
};
function pct(value) { return (value * 100).toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'; }
export default function App() {
 const [file, setFile] = useState(null);
 const [preview, setPreview] = useState('');
 const [error, setError] = useState('');
 const [busy, setBusy] = useState(false);
 const [result, setResult] = useState(null);
 useEffect(() => {
   if (!file) { setPreview(''); return; }
   const url = URL.createObjectURL(file); setPreview(url);
   return () => URL.revokeObjectURL(url);
 }, [file]);
 function choose(next) {
   setError(''); setResult(null);
   if (!next) return;
   if (!['image/jpeg', 'image/png', 'image/webp'].includes(next.type)) return setError('Selecione uma imagem JPG, PNG ou WebP.');
   if (next.size > MAX_BYTES) return setError('O arquivo excede 10 MB.');
   setFile(next);
 }
 async function analyze() {
   if (!file || !ENDPOINT) return;
   setBusy(true); setError(''); setResult(null);
   try {
     const body = new FormData(); body.append('file', file);
     const response = await fetch(ENDPOINT + '/predict', { method: 'POST', body });
     if (!response.ok) throw new Error('O servidor de inferência não concluiu a análise.');
     const data = await response.json();
     if (!data.model_version || !data.probabilities || !data.validation_status) throw new Error('Resposta incompleta do servidor.');
     if (data.validation_status !== 'validated') throw new Error('O modelo remoto ainda não foi validado para disponibilizar resultados.');
     setResult(data);
   } catch (e) { setError(e.message || 'Falha na análise.'); }
   finally { setBusy(false); }
 }
 function clear() { setFile(null);setResult(null);setError(''); }
 return <div className="app">
   <header className="topbar"><div className="brand"><span className="mark"><Activity size={23}/></span><div><strong>OCULOMICS</strong><small>Retinal AI Research</small></div></div><span className="tag"><span className="dot"/> Plataforma de pesquisa</span></header>
   <main>
     <section className="hero"><span className="eyebrow"><BrainCircuit size={15}/> INTELIGÊNCIA ARTIFICIAL & SAÚDE OCULAR</span><h1>Uma nova perspectiva sobre <em>a saúde da retina.</em></h1><p>Ambiente experimental de análise de imagens de fundo de olho. Desenvolvido para pesquisa em biomarcadores retinianos e visão computacional.</p><div className="hero-features"><span><ShieldCheck size={16}/> Pesquisa responsável</span><span><LockKeyhole size={16}/> Sem armazenamento no navegador</span><span><Stethoscope size={16}/> Não substitui avaliação médica</span></div></section>
     <div className="workspace"><section className="panel"><div className="section-head"><div className="section-icon"><FileImage size={21}/></div><div><h2>Análise de retinografia</h2><p>Envie uma imagem para iniciar</p></div><span className="step">01 / 02</span></div>
       {!file ? <label className="dropzone" onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();choose(e.dataTransfer.files?.[0]);}}><input type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>choose(e.target.files?.[0])}/><span className="upload-icon"><ArrowUpFromLine size={27}/></span><strong>Arraste sua retinografia para cá</strong><span>ou clique para selecionar no dispositivo</span><small>JPG, PNG ou WebP • até 10 MB</small></label> :
       <div className="preview-box"><img src={preview} alt="Imagem de retina selecionada para análise"/><button className="clear" onClick={clear} aria-label="Remover imagem"><X size={19}/></button><div className="filename"><CheckCircle2 size={16}/><span>{file.name}</span></div></div>}
       {error && <div role="alert" className="alert error">{error}</div>}
       <button className="primary" onClick={analyze} disabled={!file || busy || !ENDPOINT}>{busy ? 'Analisando…' : 'Analisar imagem'} <span>→</span></button>
       {!ENDPOINT && <div className="alert"><Info size={17}/> O treinamento e a API de inferência ainda não estão conectados. O upload e a visualização funcionam; resultados clínicos não são simulados.</div>}
       <p className="privacy">Uma imagem só será enviada à API externa se você clicar em Analisar e a integração estiver habilitada. Não envie dados identificáveis de pacientes sem autorização.</p>
     </section>
     <section className="panel results"><div className="section-head"><div className="section-icon"><HeartPulse size={21}/></div><div><h2>Relatório de pesquisa</h2><p>Probabilidades estimadas por modelo validado</p></div><span className="step">02 / 02</span></div>
      {!result ? <div className="empty"><span className="empty-icon"><BrainCircuit size={37}/></span><h3>Nenhuma análise disponível</h3><p>Os resultados aparecerão aqui somente após treinamento, validação e conexão com um serviço de inferência.</p><div className="subtle">Status atual: aguardando modelo validado</div></div>
      : <div className="report"><p className="model-info">Modelo {result.model_version} · Avaliação: {result.validation_status}</p>{Object.entries(result.probabilities).filter(([k,v])=>Object.hasOwn(labels,k)&&typeof v==='number'&&v>=0&&v<=1).sort((a,b)=>b[1]-a[1]).map(([key,p])=><div className="score" key={key}><div><span>{labels[key]}</span><strong>{pct(p)}</strong></div><div className="track"><span style={{width:pct(p)}}/></div></div>)}<p className="disclaimer">Probabilidades de saída do modelo para os rótulos indicados; não equivalem à probabilidade de diagnóstico confirmado. Não são uma estimativa de risco microvascular sistêmico.</p><button className="secondary" onClick={()=>window.print()}>Imprimir relatório</button></div>}
     </section></div>
     <section className="info-grid"><article><span className="info-icon"><BrainCircuit size={21}/></span><h3>Visão computacional</h3><p>Arquitetura preparada para modelos multirrótulo e pesquisa em biomarcadores da retina.</p></article><article><span className="info-icon"><Activity size={21}/></span><h3>Análise explicável</h3><p>Resultados associados à versão do modelo e a métricas de validação, sem promessas diagnósticas.</p></article><article><span className="info-icon"><ShieldCheck size={21}/></span><h3>Pesquisa responsável</h3><p>Dataset restrito nunca incorporado ao frontend público ou ao deploy da Vercel.</p></article></section>
   </main><footer>© {new Date().getFullYear()} Oculomics · Protótipo de pesquisa · Não destinado ao diagnóstico ou atendimento clínico</footer>
 </div>;
}