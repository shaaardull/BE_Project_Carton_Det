

import cv2
import os
import numpy as np
import random
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from detectron2.utils.visualizer import ColorMode


# import some common detectron2 utilities
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from detectron2.utils.logger import setup_logger
setup_logger()



cfg = get_cfg()
# add project-specific config (e.g., TensorMask) here if you're not running a model in detectron2's core library
cfg.merge_from_file('model_config.yaml')
cfg.MODEL.DEVICE = 'cpu'
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.3  # set threshold for this model
cfg.MODEL.WEIGHTS = "model_final.pth"

metadata = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])
metadata.thing_classes = ['Carton']
print("Class Names:", metadata.as_dict())
#
predictor = DefaultPredictor(cfg)


def detect_image(img_path,sample = 0):
    im = cv2.imread(img_path)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    outputs = predictor(im)
    print(outputs)
    # Get the number of instances
    num_instances = len(outputs["instances"])

    v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)

    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))

    # Increase DPI for higher resolution
    plt.figure(dpi=200)

    # Display the image using matplotlib
    plt.imshow(out.get_image()[:, :, ::-1])
    filename = os.path.basename(img_path)
    plt.savefig(f'outputs/{filename}')
    # print(filename,num_instances)
    return f'outputs/{filename}' , num_instances

# def sample_cartons(img_path):
#     im = cv2.imread(img_path)
#     im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
#     outputs = predictor(im)
#     v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
#     out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
#     # Get the number of instances
#     num_instances = len(outputs["instances"])
#     if num_instances == 0:
#         return None
#     else:
#         # Get random 20 percent cartons

