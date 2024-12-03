# HABench: Human Preference Aligned Video Generation Benchmark

HABench is a benchmark tool designed to systematically leverage MLLMs across all dimensions relevant to video generation assessment in generative models. By incorporating few-shot scoring and chain-of-query techniques, HA-Video-Bench provides a structured, scalable approach to generated video evaluation.

## Evaluation

**Multi-Dimensional Evaluation**: Supports evaluation across several key dimensions of video generation:
| Dimension  |  Code Path |
|---|---|
| Image Quality  |  `HAbench/staticquality.py` |
| Aesthetic Quality  | `HAbench/staticquality.py`  |
| Temporal Consistency | `HAbench/dynamicquality.py`  |
| Motion Effects | `HAbench/dynamicquality.py` |
| Object-Class Consistency | `HAbench/VideoTextConsistency.py` |
| Video-Text Consistency | `HAbench/VideoTextConsistency.py` |
| Color Consistency | `HAbench/VideoTextConsistency.py` |
| Action Consistency | `HAbench/VideoTextConsistency.py` |
| Scene Consistency |`HAbench/VideoTextConsistency.py` |


**Support for Multiple Video Generation Models**:
  - Lavie
  - Pika
  - Show-1
  - VideocrAfter2
  - CogVideoX5B
  - Kling
  - Gen3


## Installation Requirements

- Python >= 3.8
- OpenAI API access
   Update your OpenAI API keys in `config.json`:
   ````json
   {
       "GPT4o_API_KEY": "your-api-key",
       "GPT4o_BASE_URL": "your-base-url",
       "GPT4o_mini_API_KEY": "your-mini-api-key",
       "GPT4o_mini_BASE_URL": "your-mini-base-url"
   }
   ````

## Installation

   ````bash
   git clone https://github.com/yourusername/HABench.git
   cd HABench
   conda env create -f environment.yml
   conda activate HABench
   ````

## Data Preparation

Please organize your data according to the following structure:
```bash
/HABench/data/
├── color/                           # 'color' dimension videos
│   ├── cogvideox5b/
│   │   ├── A red bird_0.mp4
│   │   ├── A red bird_1.mp4
│   │   └── ...
│   ├── lavie/
│   │   ├── A red bird_0.mp4
│   │   ├── A red bird_1.mp4
│   │   └── ...
│   ├── pika/
│   │   └── ...
│   └── ...
│
├── object_class/                    # 'object_class' dimension videos
│   ├── cogvideox5b/
│   │   ├── A train_0.mp4
│   │   ├── A train_1.mp4
│   │   └── ...
│   ├── lavie/
│   │   └── ...
│   └── ...
│
├── scene/                           # 'scene' dimension videos
│   ├── cogvideox5b/
│   │   ├── Botanical garden_0.mp4
│   │   ├── Botanical garden_1.mp4
│   │   └── ...
│   └── ...
│
├── action/                          # 'action' 'temporal_consistency' 'motion_effects' dimension videos
│   ├── cogvideox5b/
│   │   ├── A person is marching_0.mp4
│   │   ├── A person is marching_1.mp4
│   │   └── ...
│   └── ...
│
└── overall_consistency/             # 'overall consistency' 'imaging_quality' 'aesthetic_quality' dimension videos
    ├── cogvideox5b/
    │   ├── Close up of grapes on a rotating table._0.mp4
    │   └── ...
    ├── lavie/
    │   └── ...
    ├── pika/
    │   └── ...
    └── ...
```
## Usage
Run the following command to evaluate the dimension you want to evaluate:
   ````bash
   python evaluate.py \
    --dimension $DIMENSION \
    --videos_path ./data/{dimension} \
    --config_path ./config.json/
   ````
