import os

# Run the frame-by-frame inference demo
os.system("python demo.py \
          --config-file model_config.yaml \
          --video-input input_video.mp4 \
          --confidence-threshold 0.6 \
          --output video-output.mkv \
          --opts MODEL.WEIGHTS model_final.pth ")
