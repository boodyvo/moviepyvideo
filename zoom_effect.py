import moviepy.editor as mp
import math
from PIL import Image
import numpy


def zoom_in_effect(clip, zoom_ratio=0.04):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        new_size = [
            math.ceil(img.size[0] * (1 + (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 + (zoom_ratio * t)))
        ]

        # The new dimensions must be even.
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)

        img = img.resize(new_size, Image.LANCZOS)

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = numpy.array(img)
        img.close()

        return result

    return clip.fl(effect)


def clip_from_image(image_path, duration, size):
    image_video = mp.ImageClip(image_path).set_fps(25).set_duration(duration).resize(size)
    clip = zoom_in_effect(image_video, 0.01)

    return clip


if __name__ == "__main__":
    images = [
        'out-0.png',
    ]

    slides = []
    for n, url in enumerate(images):
        slides.append(clip_from_image(url, 25))
        # slides.append(
        #     mp.ImageClip(url).set_fps(25).set_duration(25).resize(size)
        # )
        #
        # slides[n] = zoom_in_effect(slides[n], 0.01)

    video = mp.concatenate_videoclips(slides)
    video.write_videofile('zoomin.mp4')
