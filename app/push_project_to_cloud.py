import subprocess
import time

def push_image(image_name):
    while True:
        try:
            # Execute the docker push command
            result = subprocess.run(["docker", "push", image_name], check=True)
            if result.returncode == 0:
                print("Push successful!")
                break
        except subprocess.CalledProcessError as e:
            # Handle the error and retry after a delay
            print(f"Push failed: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    # Replace with your actual image name
    image_name = "gcr.io/reda-flask-monitoring/project:latest"
    push_image(image_name)
