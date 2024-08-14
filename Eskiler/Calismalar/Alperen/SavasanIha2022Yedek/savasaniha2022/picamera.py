import cv2 as cv

cap = cv.VideoCapture(0)

while True:
	ret,frame=cap.read()
	print("Return: ", ret)
	if ret:
		cv.imshow("frame", frame)
		
		cv.waitKey(1)
	
	
cap.release()
cv.destroyAllWindows()
