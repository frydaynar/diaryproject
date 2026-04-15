from settings import settings
import os

def save_graph_image(graph):
  try:
    if not os.path.exists(settings.graph_image_path):
      os.makedirs(settings.graph_image_path)
    
    png_files = [f for f in os.listdir(settings.graph_image_path) if f.endswith(".png")]
    png_count = len(png_files)
    
    new_file_name = f"graph_{png_count + 1}.png"
    
    image_data = graph.get_graph().draw_mermaid_png()
    
    save_path = os.path.join(settings.graph_image_path, new_file_name)
    with open(save_path, "wb") as f:
      f.write(image_data)
    
    print(f"성공: {save_path}에 저장되었습니다.")
  except Exception as e:
    print(f"이미지 저장 중 오류 발생: {e}")
