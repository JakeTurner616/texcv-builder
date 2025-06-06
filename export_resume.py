#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# MIT License
# 
# Copyright (c) 2025 Jakob D Turner
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import shutil
import subprocess
import requests
import sys

# Paths
OUTPUT_DIR = "output"
TEX_OUTPUT = os.path.join(OUTPUT_DIR, "resume.tex")
TEX_TEMPLATE = "jankapunkt-template/template.tex"
AVATAR_SRC_DEFAULT = "jankapunkt-template/untitled.jpg"
AVATAR_DEST = os.path.join(OUTPUT_DIR, "untitled.jpg")
SVG_ICON_DIR = "icons"

def fetch_github_avatar(username: str, save_path: str) -> bool:
    """
    Fetch the GitHub avatar for a given username and save it locally.
    Returns True if successful, False otherwise.
    """
    try:
        print(f"🔍 Fetching avatar from GitHub for user: {username}")
        res = requests.get(f"https://api.github.com/users/{username}", timeout=10)
        res.raise_for_status()
        avatar_url = res.json().get("avatar_url")
        if not avatar_url:
            print("⚠️  Avatar URL not found for GitHub user.")
            return False
        img_res = requests.get(avatar_url, timeout=10)
        img_res.raise_for_status()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(img_res.content)
        print(f"✅ Saved avatar image to: {save_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch GitHub avatar: {e}")
        return False

def convert_svgs_to_pdfs(svg_dir, output_dir):
    """
    Converts all SVG files in the given directory to PDF using Inkscape.
    """
    print("🛠️  Converting SVG icons to PDF...")
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(svg_dir):
        if filename.endswith(".svg"):
            svg_path = os.path.join(svg_dir, filename)
            pdf_filename = os.path.splitext(filename)[0] + ".pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            try:
                subprocess.run([
                    "inkscape", svg_path,
                    "--export-type=pdf",
                    "--export-filename", pdf_path
                ], check=True)
                print(f"✅ Converted {filename} → {pdf_filename}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to convert {filename}: {e}")

def save_latex_copy(template_path, output_path):
    """
    Copies the LaTeX template to the output directory.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    shutil.copy(template_path, output_path)
    print(f"📄 Copied LaTeX resume: {output_path}")

def cleanup_output_dir(output_dir, keep_file="resume.pdf"):
    """
    Deletes all files in the output directory except the specified keep_file.
    """
    print("🧹 Cleaning up temporary files...")
    for fname in os.listdir(output_dir):
        path = os.path.join(output_dir, fname)
        if fname != keep_file:
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                print(f"🗑️  Removed: {fname}")
            except Exception as e:
                print(f"⚠️  Failed to remove {fname}: {e}")

def compile_pdf(tex_path):
    """
    Compiles the LaTeX file to PDF using xelatex.
    """
    try:
        subprocess.run(
            ["xelatex", "--shell-escape", "-interaction=nonstopmode", os.path.basename(tex_path)],
            cwd=os.path.dirname(tex_path),
            check=True
        )
        print("✅ PDF built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ PDF compilation failed: {e}")

def main(github_username=None, custom_avatar_path=None):
    """
    Main build routine for resume generation.
    Downloads avatar, converts icons, compiles LaTeX, and cleans up.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    avatar_used = False
    if github_username:
        avatar_used = fetch_github_avatar(github_username, AVATAR_SRC_DEFAULT)

    avatar_to_use = custom_avatar_path if custom_avatar_path and os.path.exists(custom_avatar_path) else (
        AVATAR_SRC_DEFAULT if avatar_used or os.path.exists(AVATAR_SRC_DEFAULT) else None
    )

    if avatar_to_use:
        shutil.copy(avatar_to_use, AVATAR_DEST)
        print(f"📷 Avatar prepared at: {AVATAR_DEST}")
    else:
        print("⚠️  No avatar image available. Resume may not render properly.")

    convert_svgs_to_pdfs(SVG_ICON_DIR, OUTPUT_DIR)
    save_latex_copy(TEX_TEMPLATE, TEX_OUTPUT)
    compile_pdf(TEX_OUTPUT)
    cleanup_output_dir(OUTPUT_DIR)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Resume PDF builder.")
    parser.add_argument("--github", help="GitHub username to fetch avatar from.")
    parser.add_argument("--avatar", help="Path to local avatar image to use instead.")
    args = parser.parse_args()

    main(github_username=args.github, custom_avatar_path=args.avatar)
