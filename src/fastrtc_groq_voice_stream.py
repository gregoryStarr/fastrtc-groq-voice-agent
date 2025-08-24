import argparse
from typing import Generator, Tuple

import numpy as np
from fastrtc import (
    AlgoOptions,
    ReplyOnPause,
    Stream,
    audio_to_bytes,
)
from groq import Groq
from loguru import logger

from error_handler import patch_fastrtc_logging
from process_groq_tts import process_groq_tts
from simple_math_agent import agent as math_agent, agent_config as math_config
from astralis_support_agent import agent as support_agent, agent_config as support_config

logger.remove()
logger.add(
    lambda msg: print(msg),
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
)

groq_client = Groq()


def response(
    audio: tuple[int, np.ndarray],
) -> Generator[Tuple[int, np.ndarray], None, None]:
    """
    Process audio input, transcribe it, generate a response using LangGraph, and deliver TTS audio.

    Args:
        audio: Tuple containing sample rate and audio data

    Yields:
        Tuples of (sample_rate, audio_array) for audio playback
    """
    logger.info("🎙️ Received audio input")

    logger.debug("🔄 Transcribing audio...")
    transcript = groq_client.audio.transcriptions.create(
        file=("audio-file.mp3", audio_to_bytes(audio)),
        model="whisper-large-v3-turbo",
        response_format="text",
    )
    logger.info(f'👂 Transcribed: "{transcript}"')

    logger.debug("🧠 Running agent...")
    agent_response = support_agent.invoke(
        {"messages": [{"role": "user", "content": transcript}]}, config=support_config
    )
    response_text = agent_response["messages"][-1].content
    logger.info(f'💬 Response: "{response_text}"')

    logger.debug("🔊 Generating speech...")
    try:
        tts_response = groq_client.audio.speech.create(
            model="playai-tts",
            voice="Celeste-PlayAI",
            response_format="wav",
            input=response_text,
        )
        yield from process_groq_tts(tts_response)
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e):
            logger.warning("⚠️ TTS rate limit reached. Returning text response only.")
            # Return a simple beep or silence as fallback
            fallback_audio = np.zeros(8000, dtype=np.float32)  # 1 second of silence at 8kHz
            yield (8000, fallback_audio)
        else:
            logger.error(f"❌ TTS error: {e}")
            raise


def create_stream() -> Stream:
    """
    Create and configure a Stream instance with audio capabilities.

    Returns:
        Stream: Configured FastRTC Stream instance
    """
    return Stream(
        modality="audio",
        mode="send-receive",
        handler=ReplyOnPause(
            response,
            algo_options=AlgoOptions(
                speech_threshold=0.5,
            ),
        ),
    )


if __name__ == "__main__":
    # Patch FastRTC logging to handle connection errors gracefully
    patch_fastrtc_logging()
    
    parser = argparse.ArgumentParser(description="FastRTC Groq Voice Agent")
    parser.add_argument(
        "--phone",
        action="store_true",
        help="Launch with FastRTC phone interface (get a temp phone number)",
    )
    args = parser.parse_args()

    stream = create_stream()
    logger.info("🎧 Stream handler configured")

    if args.phone:
        logger.info("🌈 Launching with FastRTC phone interface...")
        stream.fastphone()
    else:
        logger.info("🌈 Launching with Gradio UI...")
        stream.ui.launch()
