#python create_optimized_cache_v2.py --src-dir "C:\Users\admin\Downloads\duellinks_dump\img" --dst-dir "C:\Users\admin\Downloads\duellinks_dump\img\thm"

import os
import sys
import argparse
import cv2

def parse_arguments():
    parser = argparse.ArgumentParser(description="GPU（OpenCV）を活用した超高速サムネイル生成スクリプト")
    parser.add_argument("--src-dir", "-s", required=True, help="1MBのオリジナル日本語画像が入っているフォルダパス")
    parser.add_argument("--dst-dir", "-d", default="img_cached", help="リサイズ後の軽量画像を保存するフォルダパス（初期値: img_cached）")
    parser.add_argument("--width", "-w", type=int, default=150, help="リサイズ後の横幅ピクセル（初期値: 150）")
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    if not os.path.isdir(args.src_dir):
        print(f"エラー: オリジナル画像フォルダが見つかりません: {args.src_dir}")
        sys.exit(1)
        
    # 保存先フォルダが無ければ自動作成
    os.makedirs(args.dst_dir, exist_ok=True)
    
    print(f"【設定確認】元フォルダ: {args.src_dir}")
    print(f"【設定確認】出力先フォルダ: {args.dst_dir}")
    print(f"【設定確認】リサイズ横幅: {args.width}px (縦幅は比率維持、末尾に _thm を付与)")
    print("\n【GPU加速モード】一括リサイズ処理を開始します...")
    
    success_count = 0
    error_count = 0
    
    # サポートする拡張子
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
    
    # 💡【バグ修正】os.path.splitext(f)[1] に修正し、拡張子だけを取り出して小文字比較するようにしました
    files = [f for f in os.listdir(args.src_dir) if os.path.splitext(f)[1].lower() in valid_extensions]
    total_files = len(files)
    
    if total_files == 0:
        print("対象となる画像ファイル（jpg, png等）が見つかりませんでした。")
        sys.exit(0)
        
    for filename in files:
        src_path = os.path.join(args.src_dir, filename)
        
        base_name, ext = os.path.splitext(filename)
        new_filename = f"{base_name}_thm{ext}"
        dst_path = os.path.join(args.dst_dir, new_filename)
        
        try:
            # OpenCVを使って画像を読み込み（Pillowより高速）
            img = cv2.imread(src_path)
            if img is None:
                raise ValueError("画像の読み込みに失敗しました")
                
            # 元の縦横比（アスペクト比）から縮小後の縦幅を計算
            original_height, original_width = img.shape[:2]
            ratio = args.width / float(original_width)
            target_height = int(float(original_height) * float(ratio))
            
            # 💡OpenCVの超高速なリサイズ処理（内部の並列処理・GPU支援を活用）
            # LANCZOSの代わりに、縮小に最適で高速な INTER_AREA フィルターを採用
            resized_img = cv2.resize(img, (args.width, target_height), interpolation=cv2.INTER_AREA)
            
            # JPEGの場合は画質と圧縮率を最適化して保存
            if ext.lower() in [".jpg", ".jpeg"]:
                cv2.imwrite(dst_path, resized_img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            else:
                cv2.imwrite(dst_path, resized_img)
                
            success_count += 1
            if success_count % 100 == 0 or success_count == total_files:
                print(f"進捗: {success_count} / {total_files} 枚完了...")
                
        except Exception as e:
            print(f"失敗しました ({filename}): {e}")
            error_count += 1

    print(f"\n【すべて完了しました】")
    print(f"成功: {success_count} 件 / 失敗: {error_count} 件")
    print(f"➡ 末尾に '_thm' が付いた超軽量画像が '{args.dst_dir}' に格納されました。")

if __name__ == "__main__":
    main()
