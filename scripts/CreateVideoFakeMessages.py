import os
from typing import override

import moviepy.audio.AudioClip
import numpy as np
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, VideoClip, VideoFileClip
from .CreateVideo import VideoCreator
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from .Utils import wrap_text, add_corners
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

class FakeMessages(VideoCreator):
    def __init__(self, userVoiceId: str, otherVoiceId: str):
        super().__init__()

        self.__data = super().get_data()

        load_dotenv()
        self.__elevenlabsClient = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.__userVoiceId = userVoiceId
        self.__otherVoiceId = otherVoiceId

        self.forRender = -1
        self.lastT = 0

    @override
    def create_video(self):
        """
        Function that creates a new fake messages video, based on the data provided
        :return:
        """

        #Step 1: create the fake message images
        msgImgInfo = self.__create_fake_conversation_img(self.__data)
        print(msgImgInfo)
        #Step 2: Call the elevenlabs API to generate all the voicelines
        #audioFiles = self.__generate_audio_files(self.__data["messages"])
        audioFiles = ["data/audio0.mp3", "data/audio1.mp3", "data/audio2.mp3", "image", "data/audio4.mp3", "image", "image", "data/audio7.mp3", "data/audio8.mp3", "data/audio9.mp3"]

        #Step 3: Assemble the video and audio clips
        self.__render_video(msgImgInfo, audioFiles)

    def __render_video(self, imageInfo: list[list[str | list[float]]], audioFiles: list[str]):
        """
        Renders a video using "backgroundVideo" as a background video, the images are shown continously, revealing their
        messages one by one, and the audio clips of a message are placed at the exact time that message is revealed

        :param imageInfo: A list containing elements of format [image_path, list_of_breakpoints]
        :param audioFiles: A list that contains all the paths to the audio messages
        :return: -
        """
        #Creating audio clips from audio file paths
        duration = 0 #The total duration of the video
        audioClips = []
        for audioPath in audioFiles:
            if audioPath != "image":
                audioClip = AudioFileClip(audioPath)
                audioClip.with_duration(audioClip.duration + 0.2)
            else:
                audioClip = AudioFileClip("data/PING.mp3")
                audioClip.with_duration(0.5)

            audioClips.append(audioClip)
            #duration += audioClip.duration + 0.6


        def reveal_frame(get_frame, t):
            # Get the full frame at time t (even though it’s static)
            frame = get_frame(t)

            h, w, c  = frame.shape

            if self.lastT - t > 0.5: self.forRender += 1

            init = sum([len(imageInfo[r][1]) for r in range(self.forRender)])
            st = init
            time = 0
            while st < len(audioClips) and t - time >= audioClips[st].duration:
                time += audioClips[st].duration
                st += 1

            #time += 0.5
            checkIdx = 0
            h = 0
            maxHeight = 0
            img = imageInfo[self.forRender]
            maxHeight = img[1][0]
            for el in img[1]:
                if checkIdx == st - init:
                    h = el
                    break
                maxHeight = el
                checkIdx += 1

            # Determine the current visible height based on time (from maxH to h)
            visible_height = int(maxHeight + min((t - time) / 0.2 * (h - maxHeight), (h - maxHeight)))
            self.lastT = t

            # Create a blank background
            #blank = np.full(frame.shape, 0, dtype=frame.dtype)

            if c == 3:
                # Create an RGBA frame (will be transparent where alpha=0)
                result = np.zeros((frame.shape[0], frame.shape[1], 4), dtype=np.uint8)
                # Copy RGB data from original frame for visible part
                result[:visible_height, :, :3] = frame[:visible_height, :, :3]
                # Set alpha channel to 255 (fully opaque) only for visible part
                result[:visible_height, :, 3] = 255
            else:  # If input is already RGBA
                result = np.zeros_like(frame)
                result[:visible_height, :, :] = frame[:visible_height, :, :]
                result[:visible_height, :, 3] = 255

            #blank[:visible_height, :, :] = frame[:visible_height, :, :]
            return result

        i = 0
        allClips = []
        for imgData in imageInfo:
            clipDuration = sum(map(lambda clip: clip.duration, audioClips[i:len(imgData[1]) + i]))

            chatClip = ImageClip(imgData[0], transparent=True).with_duration(clipDuration)

            newClip = chatClip.transform(reveal_frame)
            t = moviepy.audio.AudioClip.concatenate_audioclips(audioClips[i:len(imgData[1]) + i])
            newClip = newClip.with_audio(t)

            allClips.append(newClip)
            i += len(imgData[1])

        finalClip = concatenate_videoclips(allClips, method="compose", bg_color=None).with_position(("center", "center"))
        bgClip = VideoFileClip("data/minecraft.webm").with_duration(finalClip.duration)

        final = CompositeVideoClip([bgClip, finalClip], use_bgclip=True)
        # Write out the final video
        self.forRender = 0
        final.write_videofile("linear_reveal.mp4", fps=60, codec="libx264", preset="medium")

    @staticmethod
    def __create_circle_profile_pic(image: Image, profileSize: int):
        """
        Function that takes a picture, resizes it to profileSize x profileSize, then applies
        a circle mask

        :param image: (Image) An image
        :param profileSize: (Int) The size that the image will be cropped to
        :return: (Image) The new profile picture
        """

        #Resizing the image to profileSize x profileSize
        image = image.resize((profileSize, profileSize))

        #Creating the mask that will be applied to the image
        mask = Image.new("L", (profileSize, profileSize), 0)

        draw_mask = ImageDraw.Draw(mask)
        draw_mask.circle((profileSize / 2, profileSize / 2), profileSize / 2.2, fill=255)

        #Applying gaussian blur to smooth the edges of the mask
        mask = mask.filter(ImageFilter.GaussianBlur(radius=1))

        #Applying the mask to the picture (cropping it to a circle)
        profilePic = Image.new("RGBA", (profileSize, profileSize), (0, 0, 0, 0))
        profilePic.paste(image, (0, 0), mask)

        return profilePic

    @staticmethod
    def __create_bubble_message(canvas: Image.Image, text: str, font: ImageFont.truetype, padding: int, isRight: bool, position: list[int], isImage: bool):
        """
        Function that adds a bubble message on the canvas

        If "isRight" param is true, the message will be on the right side (sent),
        if it is false, the message will be on the left side (received)

        If "isImage" param is true, then the text parameter will contain the path to the image
        that will be sent/received

        :param canvas: (Image) The canvas on which the bubble will be added
        :param text: (string) The text of the message
        :param font: (ImageFont.truetype) The font used for the messages
        :param padding: (int) The padding between the text and upper/lower/left/rigt side of the bubble (inner padding)
        :param isRight: (bool) True if the message is sent, False if the message is received
        :param position: (list[int]) The first value of the list is the padding between the bubble and the left/right side, the second value is the y position of the bubble
        :param isImage: (bool) True, if the content of the message is an image
        :return: A new canvas, if the message/image would not fit in the given one, or NONE if the message/image fits
        """

        createdNewImage = False
        draw = ImageDraw.Draw(canvas)
        if isRight:
            x = canvas.width - position[0]
            y = position[1]
            anchor = "rm"
        else:
            x = position[0]
            y = position[1]
            anchor = "lm"

        if isImage:
            image = Image.open(text)

            #If the image is bigger than the maximum allowed width, then scale it to max allowed size
            if image.width > canvas.width * 0.6:
                image.resize((int(canvas.width * 0.6), int(image.height * (canvas.width * 0.6) / image.width)))

            #Rounding the corners of the image
            add_corners(image, 11)

            #Checking if the image fits in the remaining image
            if y + image.height >= canvas.height:
                createdNewImage = True
                canvas = Image.new("RGBA", canvas.size, (0, 0, 0))
                position[1] = 20
                y = 20

            if isRight:
                canvas.paste(image, (x - image.width, int(y), x, int(y + image.height)), image)
            else:
                canvas.paste(image, (x, y, x + image.width, y + image.height), image)

            position[1] += image.height
            if createdNewImage: return canvas
            else: return

        bbox = draw.multiline_textbbox((x, y), text=text, font=font, anchor=anchor)
        bbox_width = bbox[2] - bbox[0] + 2 * padding
        rows = (bbox_width - 2 * padding) // (canvas.width * 0.6) + 1

        bbox_width = min(bbox_width, canvas.width * 0.6 + 2 * padding)
        bbox_height = (bbox[3] - bbox[1]) * rows + 2 * padding + 4 * (rows - 1) # 4 * rows = LINE_SPACING

        left = x
        right = x
        upper = y
        lower = y + bbox_height

        if isRight:
            left -= bbox_width #If the message is sent, then the left bound will be = x - bbox_width
        else:
            right += bbox_width #If the message is received, then the right bound will be = x + bbox_width

        # Checking if the bubble fits in the remaining image
        if y + bbox_height >= canvas.height:
            createdNewImage = True
            canvas = Image.new("RGBA", canvas.size, (0, 0, 0))
            position[1] = 20
            y = 20

        #Drawing the bubble
        draw.rounded_rectangle((left, upper, right, lower), 20, (28, 28, 28))

        #Cropping just the created bubble and applying gaussian blur to smooth the edges
        cropBubble = canvas.crop((0, y - 10, canvas.width, canvas.height))
        cropBubble = cropBubble.filter(ImageFilter.GaussianBlur(radius=1))

        #Pasting the cropped and filtered image part back into it's place
        canvas.paste(cropBubble, (0, int(y - 10), canvas.width, canvas.height))

        #Placing the text into the bubble
        wrappedText = wrap_text(text, font, int(canvas.width * 0.6))
        draw.multiline_text((left + bbox_width / 2, upper + bbox_height / 2), text=wrappedText, font=font, fill=(255, 255, 255), anchor="mm")

        position[1] += bbox_height

        if createdNewImage:
            return canvas
        else: return

    def __create_fake_conversation_img(self, messages: dict, width=600, height=960):
        """
        Function that creates fake conversation images using the PILL library

        :param height: (int) The height of the images
        :param width: (int) The width of the images
        :param messages: (dict) A dictionary of messages and their properties(is_user: bool, is_image: bool, content: str)
        :return: A list containing elements of format [image_path, list_of_breakpoints]
        """

        # Create a black background
        image = Image.new('RGBA', (width, height), (0, 0, 0))

        draw = ImageDraw.Draw(image)

        # Draw header background
        box_width = width
        box_height = int(height * 0.15)
        box_x = 0
        box_y = 0
        draw.rectangle(
            [box_x, box_y, box_x + box_width, box_y + box_height],
            fill=(28, 28, 28)
        )

        # Opening the profile pic
        profile = Image.open("data/profile.jpg")
        PROFILE_SIZE = 85

        #Applying a circle mask to the image
        profile = self.__create_circle_profile_pic(profile, PROFILE_SIZE)

        #Calculating the x and y position for the center of the picture
        profile_x = int(box_x + (box_width - PROFILE_SIZE) / 2)
        profile_y = int(box_y + (box_height - PROFILE_SIZE) / 5)

        #Adding the profile pic to the image
        image.paste(profile, (profile_x, profile_y), profile)

        font = ImageFont.truetype("arial.ttf", 30)
        draw.text((box_width / 2, box_height * 0.9), text="Unknown", anchor="ms", font=font, align="center")

        # Creating the messages (bubbles)
        messageImages = []
        BUBBLE_DISTANCE = 20 # The distance on the y axis between bubbles
        PADDING = 20 #The inner padding between text and bubble
        bubble_pos = [25, box_height + BUBBLE_DISTANCE] # First element is the padding between the left/right side and the bubble, second element is the Y pos of the next bubble
        currentBreakPoints = [] #The values of the Y axis representing the middle-point between message bubbles/images of the current created image
        for msg in messages["messages"]:
            newCanvas = self.__create_bubble_message(canvas=image, text=msg["content"], font=font, padding=PADDING, isRight=msg["is_user"], position=bubble_pos, isImage=msg["is_image"])
            bubble_pos[1] += BUBBLE_DISTANCE

            if newCanvas:
                image.save(f"data/img{len(messageImages)}.png", format="png")
                messageImages.append([f"data/img{len(messageImages)}.png", currentBreakPoints[:]])
                image = newCanvas
                currentBreakPoints = [bubble_pos[1] - BUBBLE_DISTANCE / 2]
            else:
                currentBreakPoints.append(bubble_pos[1] - BUBBLE_DISTANCE / 2)


        image.save(f"data/img{len(messageImages)}.png", format="png")
        messageImages.append([f"data/img{len(messageImages)}.png", currentBreakPoints[:]])

        return messageImages

    def __generate_audio_files(self, messages: list):
        """
        Function that iterates through the messages dictionary and calls the elevenLabs API
        to generate text-to-speech files for every message

        :param messages: (dict) The messages that will be converted to audio
        :return: A list that contains all the paths to the audio messages
        """

        audioFilesPath = []
        for i, msg in enumerate(messages):
            if not msg["is_image"]:
                if msg["is_user"]: voiceId = self.__userVoiceId
                else: voiceId = self.__otherVoiceId

                audio = self.__elevenlabsClient.text_to_speech.convert(
                    text=msg["content"],
                    voice_id=voiceId,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128",
                )

                with open(f"data/audio{i}.mp3", "wb") as audioFile:
                    for chunk in audio:
                        audioFile.write(chunk)
                    audioFilesPath.append(f"data/audio{i}.mp3")
            else:
                audioFilesPath.append("image")

        return audioFilesPath