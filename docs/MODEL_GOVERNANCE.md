# Política de pesquisa, validação e liberação

## O que os rótulos representam
BRSET fornece rótulos de alterações retinianas. Isso não é equivalente a um desfecho validado de comprometimento microvascular sistêmico.

## Antes do treinamento
- Confirmar licença da PhysioNet, ética institucional e acesso individual.
- Manter arquivos privados; não enviar imagens de pacientes para GitHub nem Vercel.
- Separar treino, validação e teste por `patient_id`.
- Verificar distribuições e possíveis classes raras sem representação nos três conjuntos.
- Definir desfecho de interesse antes de avaliar qualquer modelo.

## Antes de publicar resultados
- Avaliar AUROC, AUPRC, sensibilidade, especificidade, calibração e intervalos de confiança no teste intocado.
- Reportar cada classe separadamente e prevalências.
- Auditar qualidade de imagem, diferentes câmeras e subgrupos demográficos.
- Validar externamente em outra população quando permitido e disponível.
- Definir supervisão médica, limites de uso e governança de liberação.
- Scores sigmoid não calibrados NÃO são probabilidades clínicas.
- Não afirmar risco sistêmico sem desfecho e validação independentes.

## Modelos de comparação planejados
1. Variáveis clínicas disponíveis e não derivadas do desfecho.
2. Biomarcadores vasculares retinianos extraídos e validados.
3. Combinação de dados clínicos e retinianos.

Os scripts disponibilizados implementam apenas um primeiro classificador de alterações retinianas, não medidas CRAE/CRVE/AVR nem risco sistêmico.

## Status de implantação
O checkpoint é salvo com `validation_status: research_only`. A API recusa servir resultados enquanto um processo independente de validação, calibração e aprovação de liberação não for concluído. Modificar manualmente esse status NÃO substitui a validação científica.
