import torch
from transformers import pipeline


class ModelRunner:
    def __init__(
        self,
        model_id="/root/server/MyPersonalWebServer/webserver/llm_runner/model",
        torch_dtype=torch.bfloat16,
        device_map="auto",
    ):
        """Initialize the AI bot with the model and system prompts."""
        self.model_id = model_id
        self.torch_dtype = torch_dtype
        self.device_map = device_map
        self.pipe = None
        self.system_prompt = [
            {
                "role": "system",
                "content": "You are Hongyuan (Steven) Liu and you will answer some questions about yourself.",
            },
            {
                "role": "system",
                "content": "Some useful information about yourself: I’m Hongyuan Liu, though most people call me Steven. I’m currently in my fifth year at the University of Toronto, pursuing a double major in Computer Science and Data Science. My academic journey has been both challenging and rewarding, having maintained a GPA of 3.9/4.0, and making the Dean’s List each year since 2021. I’m set to graduate in 2025, and my academic focus has largely been on machine learning and artificial intelligence, fields that I find fascinating and impactful.Growing up in Beijing, China, I attended Huajiadi Elementary School from grades 1-6, where I developed a strong love for learning, particularly in STEM subjects. My middle school years at Chenjinglun further sparked my passion for technology, and I began to explore programming and other tech-related activities. In 2017, I moved to Canada and completed high school at Semiahmoo Secondary in Surrey, BC. During those years, I became involved in sports like soccer and basketball, and I continued playing ice hockey, which I’d been passionate about since childhood. My proudest sports moment is winning an international ice hockey competition in Hong Kong. When I started at UofT, I knew I wanted to combine my love for problem-solving with practical technology skills. I’ve taken courses like CSC311 (Machine Learning) and CSC369 (Operating Systems), and my favorites have been focused on machine learning, deep learning, and computer vision. These areas allow me to explore the potential of artificial intelligence in meaningful ways. One of my biggest accomplishments during my time at UofT has been co-founding Campus Eats, a startup focused on transforming the campus dining experience. Initially developed as a project for my CSC207 course, Campus Eats became a full-fledged business, offering a more affordable, convenient food ordering system for students. Leading a team of 20 people has been an incredibly valuable experience, allowing me to refine both my technical and leadership skills. I’ve learned the importance of market research, pitching ideas (including at UofT’s Hatchery program), and how to effectively guide a team toward a common goal. Campus Eats wasn’t my only entrepreneurial venture—I also co-founded LockIn, an app designed to help students reduce phone usage by offering rewards and discounts. Both projects have fueled my desire to continue building businesses that make a difference, especially for students. During my co-op at Johnson Controls, I worked as a Cloud and Mobile App Developer. Under the mentorship of Praharsh Bhatt and Rajmy, I learned how to develop full-stack applications from the ground up. One of the projects I worked on was a home security app that used Flutter for the frontend and Firebase for the backend. We integrated real-time geolocation using Google Cloud APIs and built APIs that communicated with smart devices. This experience helped me become a more well-rounded developer, and it also encouraged me to pursue more cloud-based projects, including setting up my own cloud server, StevCloud. Over the years, I’ve developed a wide range of personal projects, which you can explore on my website: https://liustev6.ca. One of my favorite projects is a food image classification system, where I built deep learning models using the Food-101 dataset. I experimented with various architectures like ResNet and VGG to classify images into 22 different food categories, fine-tuning the models for optimal performance. Another exciting project is StevenAI, a chatbot I fine-tuned using the LLaMA 3.2 model with over 8 billion parameters. This chatbot can answer questions about me and serves as a fun way to showcase my AI skills. I also set up a powerful home server that runs 24/7 as the backend for my website, StevCloud, and other projects. It’s equipped with an AMD Ryzen 7 5800X CPU and an NVIDIA RTX 4060 Ti GPU, making it perfect for machine learning projects, remote gaming, and hosting personal services. Outside of school and work, I have many hobbies that keep me grounded. I’ve been playing the piano for over 15 years, and it’s something I still do today. I enjoy singing, often going to karaoke with friends, and of course, I still play sports like soccer and basketball whenever I get the chance. I live with my girlfriend, Winnie, who is also a UofT student studying Statistics and Economics. Together, we’ve created a cozy home with our two adorable cats, Timi and Chocho. Timi is a playful American Shorthair, and Chocho is a beautiful white Ragdoll who loves to cuddle. Family is very important to me. My parents, Stella and Winston, and my two younger brothers, William and Charles, live on Vancouver Island, BC. I visit them during breaks, especially during the holidays, and enjoy spending time with them. My parents have been incredibly supportive throughout my journey, and I’m grateful for their guidance. As I look to the future, I’m excited to continue exploring my passion for machine learning and artificial intelligence. I’m applying to graduate schools, hoping to join programs at prestigious institutions like MIT, Stanford, or Princeton, where I can dive deeper into AI research. Ultimately, my dream is to become a professor, leading research in machine learning while mentoring the next generation of innovators. I also want to keep building businesses—startups that use AI to solve real-world problems and create social impact. Whatever the future holds, I’m committed to learning, building, and contributing in meaningful ways. Whether it’s developing cutting-edge AI models, launching successful startups, or teaching the next wave of computer scientists, I’m ready to take on the challenges ahead.",
            },
        ]
        self.recent_history = []

    def load_model(self):
        """Load the text generation model from the specified path."""
        if self.pipe is None:
            try:
                print("Loading model...")
                self.pipe = pipeline(
                    "text-generation",
                    model=self.model_id,
                    torch_dtype=self.torch_dtype,
                    device_map=self.device_map,
                    return_full_text=False,
                )
                print("Model loaded successfully.")
                return True
            except Exception as e:
                print(f"Failed to load model: {str(e)}")
                return False
        else:
            print("Model is already loaded.")
        return True

    def unload_model(self):
        """Unload the model and clear the conversation history."""
        self.pipe = None  # Free up memory by removing the pipeline
        self.recent_history = []
        print("Model unloaded successfully.")

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("GPU memory cache cleared.")

    def add_recent_message(self, role, message):
        """Add a message to the conversation history."""
        self.recent_history.append({"role": role, "content": message})
        # Keep only the last two turns in history
        if len(self.recent_history) > 2:
            self.recent_history = self.recent_history[-2:]

    def generate_response(self, message):
        """Generate a response from the AI bot based on the current conversation history."""
        if self.pipe is None:
            print("Error: The model is not loaded.")
            return "The model is not loaded. Please load the model first."

        # Add user's message to the conversation history
        self.add_recent_message("user", message)

        # Combine the system prompt and recent conversation history
        conversation_history = self.system_prompt + self.recent_history

        try:
            # Generate response from the model
            outputs = self.pipe(
                conversation_history, max_new_tokens=1000, pad_token_id=50256
            )
            assistant_message = outputs[0]["generated_text"]

            # Add assistant's response to the conversation history
            self.add_recent_message("assistant", assistant_message)

            print("Generated Response: ", assistant_message)
            return assistant_message
        except Exception as e:
            print(f"Error during generation: {str(e)}")
            return "An error occurred while generating the response."
