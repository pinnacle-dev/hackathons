from health_bar import overlay_health_bars

def main() -> None:
    background_image_path = "./battle_bg.png"
    image_url = overlay_health_bars(
        background_image_path=background_image_path,
        enemy_health=99,
        enemy_max_health=100,
        user_health=40,
        user_max_health=100,
        output_file="final.png",
        upload=True
    )
    print(image_url)

if __name__ == "__main__":
    main()