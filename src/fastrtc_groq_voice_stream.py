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
from dynamic_agent_factory import create_custom_agent, get_voice_settings
from white_label_config import get_client_from_request

logger.remove()
logger.add(
    lambda msg: print(msg),
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>",
)

groq_client = Groq()

# Global variables for current client context
current_client_id = None
current_agent = support_agent
current_agent_config = support_config


def set_client_context(client_id: str):
    """Set the current client context for the voice agent."""
    global current_client_id, current_agent, current_agent_config
    
    if client_id:
        logger.info(f"🏷️ Setting client context: {client_id}")
        current_client_id = client_id
        current_agent, current_agent_config = create_custom_agent(client_id)
    else:
        logger.info("🏷️ Using default agent")
        current_client_id = None
        current_agent = support_agent
        current_agent_config = support_config


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
    agent_response = current_agent.invoke(
        {"messages": [{"role": "user", "content": transcript}]}, config=current_agent_config
    )
    response_text = agent_response["messages"][-1].content
    logger.info(f'💬 Response: "{response_text}"')

    logger.debug("🔊 Generating speech...")
    try:
        voice_settings = get_voice_settings(current_client_id)
        tts_response = groq_client.audio.speech.create(
            model=voice_settings["model"],
            voice=voice_settings["voice"],
            response_format=voice_settings["response_format"],
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
    parser.add_argument(
        "--client",
        type=str,
        help="Client ID for white-label configuration",
    )
    args = parser.parse_args()
    
    # Set client context if provided
    if args.client:
        set_client_context(args.client)

    stream = create_stream()
    logger.info("🎧 Stream handler configured")

    if args.phone:
        logger.info("🌈 Launching with FastRTC phone interface...")
        stream.fastphone()
    else:
        logger.info("🌈 Launching with Gradio UI...")
        stream.ui.launch()
