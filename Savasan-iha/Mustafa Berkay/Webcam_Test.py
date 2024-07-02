import cv2
import Server_Udp

def show_webcam():
    udp_sv = Server_Udp.Server()
    frame = udp_sv.create_server()  
    while True:
        frame = udp_sv.recv_frame_from_client()
        # Display the resulting frame
        cv2.imshow('Webcam', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    cv2.destroyAllWindows()

if __name__ == "__main__":
    show_webcam()
