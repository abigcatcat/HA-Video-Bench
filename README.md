# HA-Video-Bench
The repository contains the source code for **HA-Video-Bench**. To reproduce the results, you need to download necessary dependencies. 

# Evaluation Scripts
The following table contains the code path to produce evaluations under each dimension.
| Dimension  |  Code Path |
|---|---|
| Image Quality  |  `few-shot/fewscore-staticquality.py` |
| Aesthetic Quality  |   |
| Temporal Consistency | `few-shot/fewshot-dynamicquality.py`  |
| Motion Effects | |
| Object-Class Consistency | `chain of query/prompt/object_class.py` |
| Video-Text Consistency | `chain of query/prompt/overall_consistency.py` |
| Color Consistency | `chain of query/prompt/color.py` |
| Action Consistency | `chain of query/prompt/action.py` |
| Scene Consistency |`chain of query/prompt/scene.py` |
