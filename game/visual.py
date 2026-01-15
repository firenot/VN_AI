import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
from rembg import remove
import os


def generate_avatar(gender="girl",hair_lenght="long",hair_color="red",eyes_color="blue",clothes_color="black",name="Анна"):
# === Настройки ===
    MODEL_PATH = "./ai/visual/Counterfeit-V3.0_fp16.safetensors"
    CHARACTER_PROMPT = f"anime {gender}, {hair_lenght} {hair_color} hair, {eyes_color} eyes, {clothes_color} clothes"   # описание персонажа
    BACKGROUND_COLOR = "light gray"  # можно заменить на "white", "black" и т.д.
    OUTPUT_DIR = "images"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # === Загрузка модели ===
    pipe = StableDiffusionPipeline.from_single_file(
        MODEL_PATH,
        torch_dtype=torch.float16,
        safety_checker=None,
        requires_safety_checker=False
    ).to("cuda")

    # Опционально: ускорение
    pipe.enable_vae_slicing()
    generator = torch.Generator(device="cuda").manual_seed(42)
    # === Генерация ===
    prompt = (
        f"{CHARACTER_PROMPT},"
        f"medium shot, looking at viewer, "
        f"plain {BACKGROUND_COLOR} background, "
        f"character colors highly contrasting with background, "
        f"vivid clothing, distinct color palette, sharp focus, detailed face"
    )
    negative_prompt = (
        "blurry, deformed face, asymmetric eyes, extra fingers, bad anatomy, "
        "disfigured, poorly drawn face, mutation, mutated, extra limb, "
        "ugly, duplicate, morbid, mutilated, out of frame, "
        "low quality, jpeg artifacts, signature, watermark, text, username, "
        "cropped, worst quality, normal quality, "
        "colors matching background, washed out colors, dull colors, "
        "monochrome character, same color as background"
    )

    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=45,  # чуть больше шагов — лучше детали
        guidance_scale=7.0,  # чуть мягче — меньше перекосов
        width=512,
        height=1080,  # портрет по пояс
        generator=generator
    ).images[0]

    # Сохраняем оригинал
    orig_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    image.save(orig_path)

    # Удаляем фон → прозрачность
    #transparent = remove(image)  # возвращает RGBA PIL.Image
    #transparent_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    #transparent.save(transparent_path)

    print("Готово! Изображения в папке:", OUTPUT_DIR)
    return True