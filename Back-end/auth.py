from flask import Blueprint, send_file, current_app, Response, render_template, request, flash, redirect, url_for, jsonify
from datetime import *
from .models import User, Message, Images, Project
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
import json
from io import BytesIO
from PIL import Image

