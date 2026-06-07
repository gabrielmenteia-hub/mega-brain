# MEMORY: TRIBE v2 Researcher

> Atualizado: 2026-05-05

---

## Dossiers de Referência

- `knowledge/dossiers/themes/DOSSIER-BRAIN-ENCODING.md` — framework completo: paradigma atual, Algonauts 2025, TRIBE v2 findings, scaling, zero-shot generalization + seção do repo local

---

## Referências Técnicas Rápidas

### Achados-chave TRIBE v2
- **Scaling log-linear** no Courtois NeuroMod sem plateau — beneficia de mais dados
- **R_group ~0.4** — 2x acima da mediana de group-predictivity dos sujeitos
- **Zero-shot** para 695 novos sujeitos — generalização universal
- **In silico** — recupera achados de décadas de neurociência sem novos experimentos

### Achados-chave Algonauts 2025
- Todas equipes top convergiram na mesma receita (features pré-treinadas + ensembling)
- Arquitetura é irrelevante — linear model ficou em 4º
- Ensembling (20 modelos, parcel-specific) é o maior lever de performance
- "Breakthroughs may require departing from this pipeline" — MedARC

### Stack do Repo
| Componente | Versão |
|-----------|--------|
| Python | 3.11+ |
| PyTorch | >=2.5.1, <2.7 |
| x_transformers | 1.27.20 |
| moviepy | >=2.2.1 |
| License | CC BY-NC 4.0 |

### Módulos Principais
| Arquivo | Função |
|---------|--------|
| `demo_utils.py` | TribeModel — inference pública |
| `model.py` | FmriEncoder — arquitetura Transformer |
| `eventstransforms.py` | Alinhamento temporal features/TR |
| `utils_fmri.py` | Projeção superficial cortical |
| `grids/defaults.py` | Config completa de experimentos |

### Datasets
- Algonauts2025
- Lahner2024
- Courtois NeuroMod

---

## Pessoas Relacionadas

- Stéphane d'Ascoli — primeiro autor
- Jean-Rémi King — PI, Meta FAIR
- Yohann Benchetrit, Hubert Banville — co-autores
- MedARC team — Algonauts 2025 winners analysis
