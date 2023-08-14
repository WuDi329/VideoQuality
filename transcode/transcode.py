import subprocess
import os
from .capabilities import get_nvenc_capability
from . import config
import json
from .task import Task
from .video import Video
from .videotask import VideoTask
from enums import Resolution, VideoCodec, Bitrate, AudioCodec, Accelerator
import random

def read_video_info(video_path: str):
    """
        读取视频信息，返回由视频相关信息组成的对象。

        Args:
            video_path (str): 视频的路径.

        Returns:
            rate (float): 视频的帧率.
            length (float): 视频的长度.
    """
    cmd = "ffprobe -loglevel error -print_format json -show_streams {} > test.json".format(video_path)
    print("当前执行读取视频信息指令：{}".format(cmd))
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    video_info = {}
    with open("test.json", "r") as f:
        video_info = json.load(f)
    f.close()

    return extract_video_message(video_info)
    

    
    # 这里需要额外连接数据库持久化？
def extract_video_message(video_info: dict):
    """
        从视频信息中提取视频相关信息，返回由视频相关信息组成的对象。

        Args:
            video_info (dict): 视频信息.

        Returns:
            video (Video): 视频相关信息组成的对象.
    """
    width = video_info["streams"][0]["width"]
    height = video_info["streams"][0]["height"]
    video_codec = video_info["streams"][0]["codec_name"]
    bitrate = video_info["streams"][0]["bit_rate"]
    framerate = video_info["streams"][0]["r_frame_rate"]
    duration = video_info["streams"][0]["duration"]
    audio_codec=video_info['streams'][1]['codec_name'] if len(video_info['streams']) > 1 else 'none'

    print(width)
    print(height)

    resolution = ""
    if width == 1920 and height == 1080:
        resolution = Resolution.FHD
    elif width == 1280 and height == 720:
        resolution = Resolution.HD
    elif width == 640 and height == 480:
        resolution = Resolution.SD
    else:
        # 暂时不支持其他分辨率的情况
        resolution = "undefined"

    print(resolution)
    
    # 暂时只考虑hevc和h264
    video_codec = VideoCodec.H264 if video_codec == "h264" else VideoCodec.H265
    # 暂时只考虑aac和none
    audio_codec = AudioCodec.NONE if audio_codec == "none" else AudioCodec.AAC


    video = Video(resolution, video_codec, bitrate, framerate, duration, audio_codec)
    print(video)

    # 这里同样缺少video实例化的过程
    return video

def transcode(video_path: str, task: Task):
    """
        

        Args:
            video_path (str): 视频的路径.
            task (Task): 转码任务.

    """
    video = read_video_info(video_path)
    videotask = generate_videotask(video, task)
    execute_transcode(videotask)

    # video = Video(video_info["streams"][0]["r_frame_rate"], video_info["streams"][0]["duration"])

def generate_videotask(video: Video, task: Task):
    # 这里缺少数据库实例化的过程
    return VideoTask(video, task)

def read_capability():
    """
        读取capabilities.json，返回由转码能力组成的对象。

        Returns:
            capability (dict): 转码能力组成的对象.
    """
    parent_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(parent_path, "capabilities.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            capability = json.load(f)
        f.close()
    else:
        capability = get_nvenc_capability()
    return capability

def execute_transcode(videotask: VideoTask):

    outputcodec = videotask.outputcodec


    get_random_accelerator(outputcodec)
    # 获取键为'h264'的所有值

    # 打印所有值
    # print(h264_values)
    # print(outputcodec.value)


def get_random_accelerator(videocodec: VideoCodec):
    """
        从capabilities.json中随机获取一个转码能力。

        Returns:
            accelerator (Accelerator): 转码能力.
    """
    # 
    capability = read_capability()
    capability = json.loads(capability)

    accelerators = capability[videocodec.value]
    config = random.choice(accelerators)
    if config == 'software':
        config = Accelerator.software
    elif config == 'nvidia':
        config =  Accelerator.nvidia
    elif config == 'intel':
        config =  Accelerator.intel
    print(config)
    return config




# def generate_video_task(video_path: str, task: task):
#     """
#         生成视频任务，返回视频任务列表。

#         Returns:
#             video_tasks (list): 视频任务列表.
#     """



    # return float(rate.strip()), float(length.strip())/1000