from dataclasses import dataclass
from dataclasses_json import dataclass_json 

@dataclass_json
@dataclass
class Origami:
    model_name:str
    level_of_difficulty:str
    number_of_steps:int
    source_pattern:str
    creator:str
    paper_ratio:str
    video_tutorial:str
    img:str