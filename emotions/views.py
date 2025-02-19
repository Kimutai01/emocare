from django.urls import reverse
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from . models import Profile, Emotion,Plans,EmailHist,Pose
import stripe
from django.conf import settings
from django.http import JsonResponse,HttpResponse,request
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.edit import UpdateView
import numpy as np
import cv2
from emotions.forms import UpdateProfileForm
from django.utils.decorators import method_decorator
import pyaudio
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from . detection import face_emotion_detection, pose_estimation,face_recognition_function,is_standing
from speechbrain.pretrained.interfaces import foreign_class
import soundfile as sf
from django_pandas.io import read_frame
import time
from django.utils import timezone
from django.http import StreamingHttpResponse

stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://127.0.0.1:8000'

def Home(request):
    return render(request, 'home.html')

def tos(request):
    return render(request, 'term_of_service.html')

def privacy(request):
    return render(request, 'Privacy_Notice.html')


def Acceptable_Use_Notice(request):
    return render(request, 'Acceptable_Use_Notice.html')

def cookie(request):
    return render(request, 'CookiesPolicy.html')
def Accessibility(request):
    return render(request, 'Accessibility.html')
@csrf_exempt
def create_checkout_session(request):
    # plan = Plans.objects.get()
    session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {
        'currency': 'kes',
        'product_data': {
        'name': 'BASIC',
    },
    'unit_amount': 20000,
    },
    'quantity': 1,
    }],
  
    mode='payment',
    success_url=YOUR_DOMAIN + '/dashboard',
    cancel_url=YOUR_DOMAIN + '/cancel.html',
    )
    return JsonResponse({'id': session.id})

from .models import PaymentHistory # Add this

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):

    def post(self, request, format=None):
        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            print("Payment successful")
            session = event["data"]["object"]
            customer_email = session["customer_details"]["email"]
            product_id = session["metadata"]["product_id"]
            product = get_object_or_404(Product, id=product_id)

            send_mail(
                subject="Here is your product",
                message=f"Thanks for your purchase. The URL is: {product.url}",
                recipient_list=[customer_email],
                from_email="melianresearch83@gmail.com",
            )

            PaymentHistory.objects.create(
                email=customer_email, product=product, payment_status="completed"
            ) # Add this

        # Can handle other events here.

        return HttpResponse(status=200)

#home view
def home(request):
    plans = Plans.objects.all()
    
    return render(request,'plans.html', {'plans':plans})

#success view
def success(request):
 return render(request,'success.html')

 #cancel view
def cancel(request):
 return render(request,'cancel.html')

# @login_required
# def detect_face(request):
#     cap = cv2.VideoCapture(0)
#     face_recognition = []
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame_with_detected_name, detected_name = face_recognition_function(frame, image_url='https://res.cloudinary.com/dpq49zegk/image/upload/v1708240162/WhatsApp_Image_2024-02-17_at_5.58.55_PM_mzc64m.jpg', name='kilush')

#         # Print the detected name to the console
#         print(f'Detected Name: {detected_name}')

#         cv2.imshow('Face Recognition',frame_with_detected_name )

#         cv2.imshow(frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()

#     new_emotion = list(detected_name)
#     new_emotion = ['happy','ang']

#     all_emotions = Emotion.objects.all()

#     for instance in all_emotions:
#         instance.emotions += ','.join(new_emotion)  # Adding new results to the existing ones
#         instance.save()

#     return redirect('/dashboard/')




@login_required
def detect_face_emotion(request):
    detected_face_emotion = "No Faces"
    camera =cv2.VideoCapture(0)
    # Set the duration to run the loop (2 seconds)
    duration = 2
    end_time = time.time() + duration

    while time.time() < end_time:
        ret, frame = camera.read()

        # Check if the frame is empty
        if not ret or frame is None:
            print("Error: Couldn't retrieve frame from the camera.")
            break

        frame_with_detected_emotion, detected_face_emotion = face_emotion_detection(frame)

        print(f'Detected Emotion: {detected_face_emotion}')

        if time.time() >= end_time:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera resources
    camera.release()
    cv2.destroyAllWindows()

    # Get the currently logged-in user
    current_user = request.user

    emotion_mapping = {
        "Sad": 1,
        "Neutral": 3,
        "Happy": 4,
        "No Faces": 0,
        "Fear": 2
    }

    numeric_value = emotion_mapping.get(detected_face_emotion, 0)

    # Save detected emotion to the database
    save_emotion = Emotion.objects.create(
        kid=current_user,
        face_emotion=detected_face_emotion,
        probability=str(numeric_value)
    )
    save_emotion.save()

     ## Save detected emotion to the database
    save_emotion_for_email = EmailHist.objects.create(
        kid=current_user,
        timestamp=timezone.now(),
        title=detected_face_emotion,
    )
    save_emotion_for_email.save()

    # Retrieve email list
    mail_list = Profile.objects.values_list('email', flat=True)

    # Prepare email content
    html_content = render_to_string("email.html", {'emotions': detected_face_emotion})
    body = strip_tags(html_content)
    
    user_email = current_user.email

    # Send email
    message = EmailMultiAlternatives(
        "Emocare",
        body,
        '',
        [user_email],
    )
    message.attach_alternative(html_content, "text/html")
    message.send(fail_silently=False)

    return redirect('/dashboard/')



@login_required
def stream_video_feed(request):
    detected_face_emotion = "No Faces"
    camera = cv2.VideoCapture(0)    

    def generate_frames():
    
        success, frame = camera.read()
        if success:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            return (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
    def generate_frames_with_emotion():
            
            success, frame = camera.read()
            if success:
               

                # Apply face emotion detection to the frame
                frame_with_detected_emotion, detected_face_emotion = face_emotion_detection(frame)
                ret, buffer = cv2.imencode('.jpg', frame_with_detected_emotion)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                # Get the currently logged-in user
                current_user = request.user

                emotion_mapping = {
                    "Sad": 1,
                    "Neutral": 3,
                    "Happy": 4,
                    "No Faces": 0,
                    "Fear": 2
                }

                numeric_value = emotion_mapping.get(detected_face_emotion, 0)

                # Save detected emotion to the database
                save_emotion = Emotion.objects.create(
                    kid=current_user,
                    face_emotion=detected_face_emotion,
                    probability=str(numeric_value)
                )
                save_emotion.save()

                        ## Save detected emotion to the database
                save_emotion_for_email = EmailHist.objects.create(
                    kid=current_user,
                    timestamp=timezone.now(),
                    title=detected_face_emotion,
                )
                save_emotion_for_email.save()

                # Retrieve email list
                # mail_list = Profile.objects.values_list('email', flat=True)

                user_email = current_user.email
                # print(user_email)

                # Prepare email content
                html_content = render_to_string("email.html", {'emotions': detected_face_emotion})
                body = strip_tags(html_content)

                # Send email
                message = EmailMultiAlternatives(
                    "Emocare",
                    body,
                    '',
                    [user_email],
                )
                message.attach_alternative(html_content, "text/html")
                message.send(fail_silently=False)

    
     # Start the video feed
    response = HttpResponse(generate_frames_with_emotion(), content_type='multipart/x-mixed-replace; boundary=frame')

    # Redirect to 'dashhtml' URL
    return redirect('/dashboard/') 


@login_required
def detect_voice(request):
    def record_audio():
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

        print("Recording...")
        frames = []
        for i in range(0, int(RATE / CHUNK * 5)):  # Record for 5 seconds, adjust as needed
            data = stream.read(CHUNK)
            frames.append(data)

        print("Finished recording.")
    
        stream.stop_stream()
        stream.close()
        p.terminate()

        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        return audio_data

    # Function to classify emotion using pretrained model
    def classify_emotion(audio_data, temp_wav_path):
        sf.write(temp_wav_path, audio_data, 16000)

        classifier = foreign_class(source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP", pymodule_file="custom_interface.py", classname="CustomEncoderWav2vec2Classifier")
        out_prob, score, index, text_lab = classifier.classify_file(temp_wav_path)

        new_voice_emotion = list(text_lab)

        all_emotions = Emotion.objects.all()

        for instance in all_emotions:
            instance.voice_emotions += ','.join(new_voice_emotion)  # Adding new results to the existing ones
            instance.save()
     # Call the functions
    audio_data = record_audio()
    temp_wav_path = "models/microphone_recording.wav"
    emotion_label = classify_emotion(audio_data, temp_wav_path)
    return redirect('/dashboard/')

@login_required
def detect_pose(request):
    cap = cv2.VideoCapture(0)
    
    pose_label = None
    # Set the duration to run the loop (2 seconds)
    duration = 10
    end_time = time.time() + duration

    while time.time() < end_time:
        ret, frame = cap.read()

        if not ret:
            break

        frame_with_detected_pose, detected_pose = pose_estimation(frame)

        # Check if the person is in a standing pose
        standing_pose = is_standing(detected_pose)
        pose_label = "Standing" if standing_pose else "Not Standing"
        # print(f'Detected Pose: {pose_label}')

        cv2.imshow('Pose Estimation', frame_with_detected_pose)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Assuming detected_pose is not a boolean but an actual pose label (e.g., "Standing" or "Not Standing")
    print(f'Detected Pose: {pose_label}')

    # Check if pose_label is not None
    if pose_label is not None:
        new_pose = pose_label

        # #Get the currently logged-in user
        # current_user = request.user
        # save_emotion = Emotion.objects.create(
        #     kid=current_user,
        #     pose=''.join(new_pose)
        #             )
        # save_emotion.save()

        # Retrieve all instances of the Emotion model
        all_pose = Emotion.objects.all()
        # Iterate over the instances and update the pose attribute
        for instance in all_pose:
            # Check if the instance's pose attribute is not None
            if instance.pose is not None:
                instance.pose += ''.join(new_pose)  # Adding new results to the existing ones
                instance.save()
            else:
                # If the pose attribute is None, set it to the new_pose value
                instance.pose = ''.join(new_pose)
                instance.save()

    return redirect('/dashboard/')

#######################################################
#########################webcam  #######################
def webcam(request):
    return render(request, 'webcam_example.html')


############################################################################################################
#########################pose #######################
#####################################################
@login_required
def stream_pose_video_feed(request):
    camera = cv2.VideoCapture(0)
    
    def generate_frames():
        while True:
            success, frame = camera.read()
            if success:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                camera.release()
                break

    def generate_frames_with_pose():
        success, frame = camera.read()
        if success:
            frame_with_detected_pose, detected_pose = pose_estimation(frame)
            ret, buffer = cv2.imencode('.jpg', frame_with_detected_pose)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
             # Check if the person is in a standing pose
        standing_pose = is_standing(detected_pose)
        print(f'Detected Pose: {standing_pose}')
        pose_label = "Standing" if standing_pose else "Not Standing"
        print(f'Detected Pose: {pose_label}')

           # Check if pose_label is not None
        if pose_label is not None:
            new_pose = pose_label

            pose_mapping = {
                    "Standing": 1,
                    "Not standing": 0,
                  
                }
            numeric_value = pose_mapping.get(new_pose, 0)

            #Get the currently logged-in user
            current_user = request.user
            save_emotion = Pose.objects.create(
                kid=current_user,
                pose=''.join(new_pose),
                probability=str(numeric_value)

                        )
            save_emotion.save()



    response = HttpResponse(generate_frames_with_pose(), content_type='multipart/x-mixed-replace; boundary=frame')
    return redirect('/dashboard/')


def camera_view(request):
    # Open the camera
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened successfully
    if not cap.isOpened():
        raise Exception("Could not open camera")

    while True:
        # Read the current frame
        ret, frame = cap.read()

        # Convert the frame to JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)

        # Render the frame in the template
        context = {'frame': jpeg.tobytes()}
        return render(request, 'pose.html', context)

    # Release the camera
    # cap.release()

@login_required
def email_history(request):
    
    return render(request, 'email_history.html')


@login_required
def Dash(request):
    # Assuming Emotion model has a foreign key field 'kid' to associate each emotion with a user
    latest_emotion = Emotion.objects.filter(kid=request.user).last()
    all_emotions = Emotion.objects.filter(kid=request.user)

    latest_pose = Pose.objects.filter(kid=request.user).last()
    all_poses = Pose.objects.filter(kid=request.user)

    context = {
        'latest_emotion': latest_emotion,
        'all_emotions': all_emotions,
        'latest_pose': latest_pose,
        'all_poses': all_poses,
    }
    return render(request, 'dash/index.html', context)

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'profile_edit_form.html'  # Template for the form
    success_url = '/dashboard/'

    def get_object(self):
        return self.request.user.profile

def email_history(request):
    emails = EmailHist.objects.all()
    
    return render(request, 'email_history.html', {'emails':emails})

def custom_logout(request):
    logout(request)
    return redirect('/')


from emotions.voice_detection.voice_auth import enroll, recognize


def voice_auth(request):
    return render(request, 'voice_detect.html')

def enroll_route(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        uploaded_file = request.FILES.get('file')
        if name and uploaded_file:
            temp_path = 'temp_upload.wav'
            with open(temp_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            result = enroll(name, temp_path)
            return render(request, 'voice_detect.html', {'enrolled_result': "Voice successfully enrolled"})
        else:
            return render(request, 'voice_detect.html', {'error': 'Name and file are required for enrollment.'})
    else:
        return render(request, 'voice_detect.html')

def recognize_route(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            temp_path = 'temp_upload.wav'
            with open(temp_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            result = recognize(temp_path)
            print("this is the result",result)
            return render(request, 'voice_detect.html', {'result': result})
        else:
            return render(request, 'voice_detect.html', {'error': 'File is required for recognition.'})
    else:
        return render(request, 'voice_detect.html')
    
from voice_emotion_detection.main import record_audio, classify_emotion
def voice_emotion(request):
    return render(request, 'voice_emotion.html')

def classify(request):
    if request.method == 'POST':
        try:
            # Record audio
            audio_data = record_audio()

            # Save audio to a temporary file
            temp_wav_path = 'temp.wav'
            with open(temp_wav_path, 'wb') as f:
                f.write(audio_data)

            # Classify emotion
            emotion_label = classify_emotion(audio_data, temp_wav_path)
            print(emotion_label)

            # Render a template with the emotion label
            return render(request, 'voice_emotion.html', {'emotion_label': emotion_label})
        except Exception as e:
            # If any error occurs, redirect to the voice_emotion page with an error message
            return render(request, 'voice_emotion.html', {'emotion_label': str('neu')})
    else:
        # If the request method is not POST, redirect to the voice_emotion page
        return render(request, 'voice_emotion.html', {'emotion_label': str(e)})
