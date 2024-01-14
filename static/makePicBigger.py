from PIL import Image

# Open the image
image = Image.open('/Users/tarik0219/Documents/dev/CollegeBasketballApp/CollegeBasketballAnalytics/static/CBB-AI-COM.png')

# Define the desired size
new_size = (image.width * 2, image.height * 2)

# Resize the image
resized_image = image.resize(new_size, Image.ANTIALIAS)

# Save the resized image
resized_image.save('/Users/tarik0219/Documents/dev/CollegeBasketballApp/CollegeBasketballAnalytics/static/tshirt_resized.png')
