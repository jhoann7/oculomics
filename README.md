# Oculomics

**Plataforma experimental de pesquisa em inteligência artificial aplicada a retinografias.** Interface web com upload de imagem e espaço para resultados provenientes de modelos *realmente treinados, avaliados e liberados*. Dataset de referência: **Brazilian Multilabel Ophthalmological Dataset (BRSET), v1.0.2**, disponibilizado pela PhysioNet.

> **Atenção — estado atual (MVP):** o site está preparado para publicação na Vercel, mas **não possui um modelo treinado/validado conectado**. Não há qualquer porcentagem simulada. A inferência só é habilitada com API configurada e modelo explicitamente liberado. A aplicação não é um dispositivo médico e não deve orientar diagnóstico, tratamento ou decisões clínicas.

## 1. Objetivo científico

Investigar características retinianas associadas a alterações microvasculares e, futuramente, avaliar o valor incremental de biomarcadores extraídos de fotografias de fundo de olho quando combinados a variáveis clínicas para um **desfecho sistêmico definido e validado independentemente**.

**Importante:** o BRSET contém rótulos de alterações oftalmológicas, não um rótulo validado de comprometimento microvascular sistêmico. Diagnósticos como diabetes e hipertensão não são substitutos automáticos desse desfecho. Não se deve usar a mesma informação para definir o desfecho e alimentá-la como preditora.

### Fases de pesquisa

1. Auditoria e organização dos dados; verificação de imagens e rótulos.
2. Classificador **multirrótulo** de alterações retinianas (baseline experimental).
3. Segmentação vascular; distinção entre artérias e veias; validação em conjuntos apropriados.
4. Extração de CRAE, CRVE, AVR, tortuosidade, densidade, ramificações e dimensão fractal, quando tecnicamente validável.
5. Definição de desfecho clínico sistêmico, avaliação de três modelos: **clínico**, **retiniano** e **combinado**.
6. Testes externos, calibração, análise de subgrupos, avaliação clínica e governança.

A estrutura atual implementa as fases iniciais, **não** a medição validada dos biomarcadores microvasculares nem a predição de risco sistêmico.

## 2. Estrutura do repositório

```text
oculomics/
├── src/
│   ├── App.jsx                 # Upload, prévia e relatório condicionado à API
│   ├── main.jsx                # Entrada da aplicação
│   └── styles.css              # Interface responsiva
├── ml/
│   ├── requirements.txt        # Dependências do pipeline Python
│   ├── common.py               # Rótulos BRSET e utilitários
│   ├── audit.py                # Auditoria desidentificada/agregada
│   ├── prepare.py              # Divisão por paciente: treino/validação/teste
│   ├── train.py                # ResNet18 multirrótulo, baseline de pesquisa
│   └── serve.py                # API privada FastAPI (bloqueada sem validação)
├── scripts/
│   └── diagnosis_manifest.py   # Índices locais por diagnóstico
├── docs/
│   └── MODEL_GOVERNANCE.md     # Critérios de liberação e boas práticas
├── .env.example
├── .gitignore                  # Exclui dados, checkpoints e relatórios privados
├── index.html
├── package.json
├── vercel.json
└── vite.config.js
```

## 3. Tecnologias

- **Frontend:** React 18, Vite 6, CSS responsivo, lucide-react.
- **Pesquisa/IA:** Python, Pandas, PyTorch, torchvision, scikit-learn, Pillow.
- **Inferência futura:** FastAPI hospedada em infraestrutura privada, separada da Vercel.
- **Hospedagem:** Vercel para interface estática.
- **Armazenamento de dados:** diretório privado autorizado, não o repositório nem o frontend.

## 4. Executar o frontend localmente

Pré-requisito: Node.js compatível com o Vite 6 (recomenda-se Node.js 20 LTS ou superior).

```bash
npm install
npm run dev
```

Abra o endereço apresentado pelo terminal (normalmente `http://localhost:5173`).

Para gerar a versão de produção:

```bash
npm run build
npm run preview
```

O frontend aceita arquivos JPG/PNG/WebP até 10 MB, exibe prévia e só tenta inferência quando `VITE_INFERENCE_API_URL` estiver configurada. Nenhum resultado é inventado.

## 5. Publicação na Vercel

1. Acesse [vercel.com](https://vercel.com), entre com GitHub e selecione **Add New → Project**.
2. Importe **jhoann7/oculomics**.
3. Confirme **Framework Preset: Vite**, **Root Directory: .**, **Build Command: `npm run build`** e **Output Directory: `dist`**.
4. Faça o deploy. O arquivo `vercel.json` já contém a configuração de SPA.
5. **Não configure `VITE_INFERENCE_API_URL` por enquanto**: isso mantém o site em modo protótipo sem afirmações preditivas.
6. Quando a API validada existir, configure `VITE_INFERENCE_API_URL=https://sua-api-privada.example`, configure CORS no servidor e faça novo deploy. Variáveis prefixadas com `VITE_` são **públicas no bundle**: jamais coloque senhas ou tokens nelas.

**A Vercel hospeda o frontend, não treina o modelo.** O treinamento PyTorch deve ocorrer em máquina com recursos adequados, offline ou em ambiente privado que respeite a licença da PhysioNet.

## 6. BRSET: organização privada

Fonte: [PhysioNet BRSET 1.0.2](https://physionet.org/content/brazilian-ophthalmological/1.0.2/).

Conteúdo original: `label_brset.csv`, `SHA256SUMS.txt`, licença e fotografias `fundus_photos/img00001.jpg`, etc.

**Atenção:** dados BRSET são de acesso restrito. **Não suba o CSV individual, as imagens, manifests com identificadores, checkpoints nem relatórios individuais ao GitHub público, à Vercel ou a serviços públicos sem autorização explícita.** Mantenha controle de acesso e armazenamento seguro. Cada colaborador precisa obedecer às próprias permissões/licença.

Exemplo de organização **local e privada**:

```text
dados-privados/
├── label_brset.csv
├── SHA256SUMS.txt
└── fundus_photos/
    ├── img00001.jpg
    └── ...
```

### Auditar a base

Na pasta `ml`, crie um ambiente Python privado, instale as dependências e execute:

```bash
python -m pip install -r requirements.txt
python audit.py --csv ../dados-privados/label_brset.csv --images ../dados-privados/fundus_photos
```

O relatório `outputs/audit.json` reúne apenas estatísticas agregadas. O arquivo não é publicado automaticamente.

### Separar por paciente antes do treinamento

```bash
python prepare.py --csv ../dados-privados/label_brset.csv --images ../dados-privados/fundus_photos
```

O split é feito **por `patient_id`**, impedindo que imagens do mesmo paciente estejam em treino e teste. A divisão usa 70%/10%/20% aproximadamente por número de pacientes; devido ao agrupamento, os percentuais em imagens podem variar.

**Limitação:** o split inicial é aleatório por grupos, **não é estratificado multirrótulo**. Classes raras (por exemplo, descolamento de retina) podem ficar sem positivos na validação ou teste; revise o relatório antes de aceitar o desenho amostral. Não mova imagens manualmente entre conjuntos após ver os resultados.

### Treinar baseline de classificação

```bash
python train.py --images ../dados-privados/fundus_photos --splits outputs/splits --epochs 8
```

O script usa ResNet18 pré-treinada com 13 saídas sigmoid e perda `BCEWithLogitsLoss`. A validação registra AUROC e AUPRC por classe quando calculáveis. O dataset de teste é preservado para avaliação posterior; este script **não executa a avaliação final no teste**, nem calibração, nem validação clínica.

Saída privada em `outputs/model/`: `resnet18_brset.pt`, `validation_metrics.json` e `model_card.json`. A versão criada recebe `validation_status: research_only`; **não deve ser tratada como pronta para implantação pública.**

### Categorias por diagnóstico (multirrótulo)

Na raiz do repositório, em ambiente privado com dependência `pandas`:

```bash
python scripts/diagnosis_manifest.py --labels dados-privados/label_brset.csv --images dados-privados/fundus_photos
```

O script cria pastas de diagnóstico **com arquivos `manifest.csv`**, em vez de duplicar milhares de fotografias: uma mesma imagem pode aparecer em mais de um diagnóstico, e alguns pacientes têm ambas as retinas registradas. **Os manifestos são dados restritos** e estão sob `outputs/`, excluídos do Git.

**Para testar modelos:** faça primeiro o split por paciente; os grupos de diagnóstico não substituem um conjunto de teste independente. Não use imagens do mesmo paciente simultaneamente no treino e no teste.

## 7. Integração futura do modelo

Contrato HTTP esperado pela interface:

- `POST /predict` — multipart/form-data com campo `file` (JPG/PNG/WebP, até 10 MB).
- Retorno JSON apenas de uma API autorizada com versão e status de validação confirmados:

```json
{
  "model_version": "versao-validada",
  "validation_status": "validated",
  "probabilities": {
    "diabetic_retinopathy": 0.12,
    "macular_edema": 0.04
  }
}
```

**Este JSON é somente um exemplo de formato de API, não resultado obtido com imagens reais.**

Probabilidades brutas da camada sigmoid são scores de classificação; **não** implicam automaticamente probabilidade de diagnóstico, risco sistêmico ou confiança clínica. Precisam de calibração, validação externa, controle de qualidade e avaliação por especialistas antes de qualquer linguagem clínica.

O arquivo `ml/serve.py` demonstra uma API que recusa predições quando o `model_card.json` não está liberado. A liberação **não** consiste apenas em mudar uma flag; requer validação e governança independente documentadas em `docs/MODEL_GOVERNANCE.md`.

**Segurança em produção:** a API deve exigir autenticação, HTTPS, limites de requisição e políticas de retenção, com autorização para processar quaisquer imagens enviadas; o exemplo FastAPI ainda não implementa esses controles e não deve ser exposto publicamente.

## 8. Critérios mínimos de pesquisa

- Controle de qualidade de imagens e verificação do manifesto SHA-256.
- Divisão por paciente; acompanhamento da frequência de rótulos em cada subconjunto.
- Controle de desbalanceamento, dados faltantes e diferenças entre câmeras.
- Métricas por classe e intervalos de confiança (especialmente classes raras).
- Limiar e calibração definidos apenas na validação, sem examinar o teste para ajustar o modelo.
- Teste final intocado e validação externa, quando viável.
- Revisão médica e regras éticas locais para qualquer investigação com dados de pacientes.

## 9. Segurança, privacidade e licença

A documentação da PhysioNet impõe restrições de compartilhamento, proteção de dados, finalidade científica e credenciamento individual. Código de pesquisa pode ser aberto, mas **não deve incluir dados restritos**.

Não envie imagens com informações identificáveis, use HTTPS e garanta permissão para qualquer processamento externo. O protótipo não mantém histórico local nem salva o arquivo enviado, mas o envio para uma API futura requer política de privacidade e armazenamento do lado do servidor.

## 10. Status real dos componentes

| Componente | Status |
|---|---|
| Frontend e upload/preview | Implementado |
| Configuração para build Vite/Vercel | Implementada |
| Auditoria BRSET e divisão por paciente | Scripts implementados; execução com imagens pendente |
| Manifestos locais multirrótulo | Script implementado; execução pendente |
| Treinamento ResNet18 inicial | Script implementado; **não executado** |
| Pesos treinados e testados | **Indisponíveis** |
| API pública de inferência | **Não habilitada** |
| Extração CRAE/CRVE/AVR | Planejada, não implementada |
| Risco microvascular sistêmico | Pesquisa futura dependente de desfecho válido |
| Validação externa | Pendente |

## 11. Referência de dados

BRSET: https://physionet.org/content/brazilian-ophthalmological/1.0.2/

Leia também: `docs/MODEL_GOVERNANCE.md`.

---

**Oculomics** · Desenvolvimento experimental de software e pesquisa em inteligência artificial, visão computacional e saúde ocular. **Não é uma ferramenta aprovada para diagnóstico.**


## 12. Organização de atalhos no Google Drive (opcional; execução na conta autorizada)

A pasta privada de categorias já foi criada no Drive e contém 13 subpastas de diagnóstico. Como o BRSET é multirrótulo, **não mova as fotos originais**: uma mesma imagem pode ter múltiplas categorias. O arquivo `scripts/drive_organize.gs` cria **atalhos** para os originais, sem duplicar seu conteúdo.

Para aplicar na própria conta autorizada:

1. Abra [script.google.com](https://script.google.com), crie um projeto privado e cole o conteúdo de `scripts/drive_organize.gs`.
2. Em **Project Settings → Script properties**, registre `BRSET_CSV_ID` (ID do CSV privado no Drive), `BRSET_IMAGES_ID` (ID da pasta privada com as imagens originais) e `BRSET_DIAGNOSES_ID` (ID da pasta privada de categorias criada no Drive).
3. Execute `organizeNextBatch` e autorize apenas as permissões necessárias. Repita a execução enquanto o registro indicar novos lotes. O script processa até 100 arquivos originais por chamada e guarda o cursor de continuação nas propriedades do projeto.
4. Confirme manualmente uma amostra das associações de categoria com o CSV; avalie os casos não encontrados. A listagem de categorias **não** é divisão treino/teste.

**Status:** pastas criadas; os milhares de atalhos ainda **não foram gerados**, pois a execução do Apps Script requer autorização na sua conta Google. Não publique IDs de pastas, credenciais ou a base restrita. Os atalhos herdam permissões dos arquivos originais; não amplie o compartilhamento das pastas de diagnóstico.

