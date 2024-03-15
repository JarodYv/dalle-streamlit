from openai import OpenAI
import streamlit as st
import requests
import zipfile
import io
# from utils import icon
from streamlit_image_select import image_select

# UI configurations
st.set_page_config(page_title="Replicate Image Generator",
                   page_icon=":bridge_at_night:",
                   layout="wide")
# icon.show_icon(":foggy:")
st.markdown("# :rainbow[谱蓝文生图艺术工坊]")

API_KEY = st.secrets["API_KEY"]
client = OpenAI(api_key=API_KEY)

# Placeholders for images and gallery
generated_images_placeholder = st.empty()
gallery_placeholder = st.empty()


def configure_sidebar():
    """
    Setup and display the sidebar elements.

    This function configures the sidebar of the Streamlit application, 
    including the form for user inputs and the resources section.
    """
    with st.sidebar:
        with st.form("my_form"):
            st.info("**请开始你的创作 ↓**", icon="👋🏾")
            with st.expander(":orange[**参数设置**]"):
                # Advanced Settings (for the curious minds!)
                img_size = st.selectbox('图片尺寸', ('1024x1024', '1024x1792', '1024x1792'))
                img_quality = st.selectbox('图片质量', ('standard', 'hd'))
            prompt = st.text_area(
                ":orange[**输入提示词**]",
                value="Flat designed logo with white background featuring a stylized [dragon] with an aggressive expression, vibrant and dynamic, with light colors and sharp geometric shapes. [dragon] appears fierce and formidable, embodying the spirit of competitive gaming.")
            # The Big Red "Submit" Button!
            submitted = st.form_submit_button(
                "提交", type="primary", use_container_width=True)

        return submitted, img_size, img_quality, prompt


def main_page(submitted: bool, img_size: str, img_quality: str, prompt: str) -> None:
    """Main page layout and logic for generating images.

    Args:
        submitted (bool): Flag indicating whether the form has been submitted.
        img_size (str): Scheduler type for the model.
        img_quality (str): Text prompt for elements to avoid in the image.
        prompt (str): Text prompt for the image generation.
    """
    if submitted:
        with st.status('👩🏾‍🍳 正在将你的创意变成艺术...', expanded=True) as status:
            st.write("⚙️ 模型初始化成功")
            st.write("🙆‍♀️ 请稍等片刻")
            try:
                # Only call the API if the "Submit" button was pressed
                if submitted:
                    # Calling the replicate API to get the image
                    with generated_images_placeholder.container():
                        all_images = []  # List to store all generated images
                        response = client.images.generate(
                            model="dall-e-3",
                            prompt=prompt,
                            size=img_size,
                            quality=img_quality,
                            n=1,
                        )
                        image_url = response.data[0].url
                        if image_url:
                            st.toast('图片生成完成！', icon='😍')
                            # Save generated image to session state
                            st.session_state.generated_image = [image_url]

                            # Displaying the image
                            for image in st.session_state.generated_image:
                                with st.container():
                                    st.image(image, caption="请欣赏 AI 生成的图片 🎈",
                                             use_column_width=True)
                                    # Add image to the list
                                    all_images.append(image)

                                    response = requests.get(image)
                        # Save all generated images to session state
                        st.session_state.all_images = all_images

                        # Create a BytesIO object
                        zip_io = io.BytesIO()

                        # Download option for each image
                        with zipfile.ZipFile(zip_io, 'w') as zipf:
                            for i, image in enumerate(st.session_state.all_images):
                                response = requests.get(image)
                                if response.status_code == 200:
                                    image_data = response.content
                                    # Write each image to the zip file with a name
                                    zipf.writestr(
                                        f"output_file_{i + 1}.png", image_data)
                                else:
                                    st.error(
                                        f"Failed to fetch image {i + 1} from {image}. Error code: {response.status_code}",
                                        icon="🚨")
                        # Create a download button for the zip file
                        st.download_button(
                            ":red[**下载图片**]", data=zip_io.getvalue(), file_name="output_files.zip",
                            mime="application/zip", use_container_width=True)
                status.update(label="✅ 图片生成完成!",
                              state="complete", expanded=False)
            except Exception as e:
                print(e)
                st.error(f'出错了: {e}', icon="🚨")

    # If not submitted, chill here 🍹
    else:
        pass

    # Gallery display for inspo
    with gallery_placeholder.container():
        st.markdown("""
            文生图最常用的提示框架为 **OSED**：
            * O: Object，对象，说明想要绘制的是什么。例如图表、海报、插画
            * S: Style，风格，描述期望的绘画风格
            * E: Element，元素，描述图像中需要的元素
            * D: Detail，细节，详细描述元素之间的关系以及元素的细节
            必要时，还可以给出关键词进行补充描述。
            
            下面是一些提示词示例：
            1. Flat designed logo with white background featuring a stylized [dragon] with an aggressive expression, vibrant and dynamic, with light colors and sharp geometric shapes. [dragon] appears fierce and formidable, embodying the spirit of competitive gaming.
            2. detailed logo design on a white background with the word ["Class 3"] written in a colorful bold font decorated by Olympic decorations with light color
            3. sport logo, eagle, Isometric illustration, synthwave palette, dark plain background, with the large text "CLASS 3" incorporated.
            4. a sports team logo of a [tiger] with white background, the text ["Class 3"] written in a bold colorful font under the logo
            5. a gold/blue metal texture geometric [eagle], sports brand logo opening its wings like a phoenix with feathers around, white background, and the word ["Class3"] in a bold colorful font, cinematic, poster, vibrant.
            
            > 注意，一般来说，在文生图中，英文提示词比中文提示词效果明显要好。
        """)
        img = image_select(
            label="下面是一下示例 😉",
            images=[
                "gallery/logo112.png",
                "gallery/logo117.png", "gallery/logo121.png",
                "gallery/logo128.png", "gallery/logo139.png",
            ],
            captions=["示例1",
                      "示例2",
                      "示例3",
                      "示例4",
                      "示例5",
                      ],
            use_container_width=True
        )


def main():
    """
    Main function to run the Streamlit application.

    This function initializes the sidebar configuration and the main page layout.
    It retrieves the user inputs from the sidebar, and passes them to the main page function.
    The main page function then generates images based on these inputs.
    """
    submitted, img_size, img_quality, prompt = configure_sidebar()
    main_page(submitted, img_size, img_quality, prompt)


if __name__ == "__main__":
    main()
