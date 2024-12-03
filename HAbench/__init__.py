import os
import importlib
from pathlib import Path
from .utils import save_json, load_json

class HABench(object):
    def __init__(self, full_info_dir, output_path, config_path):
        """
        Initialize VBench evaluator
        
        Args:
            full_info_dir (str): Path to the full info JSON file
            output_path (str): Directory to save evaluation results
            config_path (str): Path to configuration file
        """
        self.full_info_dir = full_info_dir  
        self.output_path = output_path
        self.config_path = config_path
        self.config = load_json(config_path)
        os.makedirs(self.output_path, exist_ok=True)

    def build_full_dimension_list(self):
        """Return list of all available evaluation dimensions"""
        return [
           "aesthetic_quality", "imaging_quality", "temporal_consistency", "motion_effects", 
           "color", "object_class", "scene", "action", "overall_consistency"
        ]

    def evaluate_dimension(self, dimension):
        """
        Evaluate a single dimension by importing and running its module
        
        Args:
            dimension (str): Name of the dimension to evaluate
            
        Returns:
            dict: Results of the evaluation
        """
        try:
            # Import the dimension's module
            VideoTextConsistency_dimensions = ['color', 'object_class', 'scene', 'action', 'overall_consistency']
            static_dimensions = ['aesthetic_quality', 'imaging_quality']
            dynamic_dimensions = ['temporal_consistency', 'motion_effects']

            if dimension in VideoTextConsistency_dimensions:
                from .VideoTextConsistency import eval
                from .prompt_dict import prompt
                results = eval(self.config, prompt[dimension],dimension)
            elif dimension in static_dimensions:
                from .staticquality import eval
                from .prompt_dict import prompt
                results = eval(self.config, prompt[dimension],dimension)
            elif dimension in dynamic_dimensions:
                from .dynamicquality import eval
                from .prompt_dict import prompt
                results = eval(self.config, prompt[dimension],dimension)
            else:
                raise ValueError(f"Unknown dimension: {dimension}")
            
                
            return results
            
        except Exception as e:
            print(f"Error evaluating {dimension}: {e}")
            return {'error': str(e)}

    def evaluate(self, videos_path, name, prompt_list=[], dimension_list=None, **kwargs):
        """
        Run evaluation on specified dimensions
        
        Args:
            videos_path (str): Path to video files
            name (str): Name for this evaluation run
            prompt_list (list): List of prompts
            dimension_list (list): List of dimensions to evaluate
            **kwargs: Additional arguments
        """
        # Initialize results dictionary
        VideoTextConsistency_dimensions = ['color', 'object_class', 'scene', 'action', 'overall_consistency']
        static_dimensions = ['aesthetic_quality', 'imaging_quality']
        dynamic_dimensions = ['temporal_consistency', 'motion_effects']

        
        # Use default dimension list if none provided
        if dimension_list is None:
            dimension_list = self.build_full_dimension_list()
            print(f'Using default dimension list: {dimension_list}')
        
        # Evaluate each dimension
        for dimension in dimension_list:
            print(f"Evaluating {dimension}...")
            results = self.evaluate_dimension(dimension)

            # 为每个维度创建输出目录
            dimension_output_dir = os.path.join(self.output_path, dimension)
            os.makedirs(dimension_output_dir, exist_ok=True)
            
            # 保存结果
            if dimension in VideoTextConsistency_dimensions:
                save_json(results['history'], os.path.join(dimension_output_dir, f'{name}_history_results.json'))
                save_json(results['updated_description'], os.path.join(dimension_output_dir, f'{name}_updated_description_results.json'))
                save_json(results['score'], os.path.join(dimension_output_dir, f'{name}_score_results.json'))
            else:
                save_json(results['score'], os.path.join(dimension_output_dir, f'{name}_score_results.json'))
        
        return results
