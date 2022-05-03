import logging
import os
import argparse
from endpoints import smtp
from videostreamdetector import VideoStreamDetector

DEFAULT_MODEL_PATH = "./models/lite-model_efficientdet_lite0_detection_metadata_1.tflite"
DEFAULT_SUBJECT = "Neuer Vogel gesichtet!"
DEFAULT_TEXT = "Ein neuer Vogel wurde gesichtet. Siehe Video im Anhang. Diese Nachricht wurde automatisch erstellt."

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument("--rtsp_url", type=str, help="URL to the RTSP video stream of the camera.")
    parser.add_argument("--model_weights_path", type=str, default=DEFAULT_MODEL_PATH,
                        help="URL to the RTSP video stream of the camera.")
    parser.add_argument("--object_to_detect", type=str, default="bird", help="Class to detect.")
    parser.add_argument("--pause_on_detection", type=float, default=30,
                        help="Number of seconds to pause the processing for when an object got detected.")
    parser.add_argument("--pause_after_processing", type=float, default=1,
                        help="Number of seconds to pause after each processing.")
    parser.add_argument("--video_sequence_length", type=float, default=5,
                        help="Number of seconds to record after an object detection event.")
    parser.add_argument("--restart_time", type=float, default=120,
                        help="Number of seconds after which to restart the video stream.")
    parser.add_argument("--detection_threshold", type=float, default=0.5, help="Detection confidence threshold.")
    parser.add_argument("--max_detection_count", type=int, default=3, help="Max object detection count per frame.")
    parser.add_argument("--detector_threads", type=int, default=4, help="Number of CPU threads for the detector.")
    parser.add_argument("--debug", action="store_true", help="Enter debug mode.")
    parser.add_argument("--sender_mail", type=str, help="Email Account used for sending mails.")
    parser.add_argument("--sender_pw", type=str, help="Password of the sending account.")
    parser.add_argument("--recipient_mails", type=str, nargs="+", help="List of mail recipients.")
    parser.add_argument("--smtp_server", type=str, default="smtp.gmail.com", help="SMTP Email Server address.")
    parser.add_argument("--smtp_port", type=int, default=587, help="SMTP Email Server port.")
    parser.add_argument("--subject", type=str, default=DEFAULT_SUBJECT, help="Email subject.")
    parser.add_argument("--text", type=str, default=DEFAULT_TEXT, help="Email text.")
    parser.add_argument("--video_fps", type=int, default=30, help="FPS for saving the video.")
    args = parser.parse_args()


    def send_video_then_delete(video_file_path: str):
        smtp.send_mail(recipient_mails=args.recipient_mails,
                       subject=args.subject,
                       text=args.text,
                       server=args.smtp_server,
                       port=args.smtp_port,
                       sender_mail=args.sender_mail,
                       sender_mail_pw=args.sender_pw,
                       attachment_path=video_file_path)
        logging.info(f"Sending video per mail to: {', '.join(args.recipient_mails)}.")
        os.remove(video_file_path)


    stream = VideoStreamDetector(rtsp_url=args.rtsp_url,
                                 rtsp_buff_size=2,
                                 model_weights_path=args.model_weights_path,
                                 class_to_detect=args.object_to_detect,
                                 callback=send_video_then_delete,
                                 pause_after_detection=args.pause_on_detection,
                                 pause_after_processing=args.pause_after_processing,
                                 video_sequence_length=args.video_sequence_length,
                                 restart_time=args.restart_time,
                                 detection_threshold=args.detection_threshold,
                                 max_detection_count=args.max_detection_count,
                                 detector_threads=args.detector_threads,
                                 video_fps=args.video_fps,
                                 debug=args.debug)

    while True:
        try:
            stream.start()
        except Exception as e:
            logging.error(e)
