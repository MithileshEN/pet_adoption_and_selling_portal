from flask import Flask, render_template, request, redirect, url_for,send_from_directory,jsonify
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
import openai

openai.api_key = "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"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")  
db = client["pets_portal"]  

class Pet:
    def __init__(self, name, species, age):
        self.name = name
        self.species = species
        self.age = age

# Add Pet for Sale
@app.route('/add_pet_for_sale', methods=['GET', 'POST'])
def add_pet_for_sale():
    if request.method == 'POST':
        name = request.form['name']
        species = request.form['species']
        age = request.form['age']
        characteristics = request.form['characteristics']
           
        # Handle file upload
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

        pet_for_sale = {
            'name': name,
            'species': species,
            'age': age,
            'characteristics':{
            "personality": request.form.get("personality"),
            "breed_preference": request.form.get("breed_preference"),
            "pet_parenting": request.form.get("pet_parenting"),
            "climate_zone": request.form.get("climate_zone"),
            "dog_space": request.form.get("dog_space"),
            "allergic_to_hair": request.form.get("allergic_to_hair"),
            "aggressive_friendly": request.form.get("aggressive_friendly"),
            "financial_considerations": request.form.get("financial_considerations"),
            "noise_tolerance": request.form.get("noise_tolerance"),
            "experience": request.form.get("experience"),
            "time_commitment": request.form.get("time_commitment"),
            },
            
            'image': filename,
            'contact':request.form.get('contact'),
        }

        db.pets_for_sale.insert_one(pet_for_sale)  
        return redirect(url_for('view_pets_for_sale'))

    return render_template('add_pet_for_sale.html')

# View Pets for Sale
@app.route('/view_pets_for_sale')
def view_pets_for_sale():
    pets_for_sale = db.pets_for_sale.find()
    return render_template('view_pets_for_sale.html', pets_for_sale=pets_for_sale)

# Index Page
@app.route('/')
def index():
    pets = db.pets.find()
    return render_template('index.html', pets=pets)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/find_clinics', methods=['GET', 'POST'])
def find_clinics():
    if request.method == 'POST':
        locality = request.form['locality']
        city = request.form['city']

        # Find clinics with the same locality
        clinics_in_locality = db.clinics.find({"address.locality": locality})
        
        # Find clinics in the same city but different locality
        clinics_in_city = db.clinics.find({
            "address.locality": {"$ne": locality},
            "address.city": city
        })

        return render_template('clinics.html', clinics_in_locality=clinics_in_locality, clinics_in_city=clinics_in_city)

    return render_template('find_clinics.html')




@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    conversation = []  

    if request.method == 'POST':
        user_query = request.form['user_query']

        
        response = pet_care_responses.get(user_query, "I'm sorry,Based on my knowledge base I can't provide a specific answer to that question.")

        
        conversation.append(("user", user_query))
        conversation.append(("chatbot", response))

        
        

    return render_template('chatbot.html', conversation=conversation)




# Weights for compatibility calculation
WEIGHTS = {
    "personality": 2,
    "breed_preference": 3,
    "pet_parenting": 1,
    "climate_zone": 1,
    "dog_space": 2,
    "allergic_to_hair": 1,
    "aggressive_friendly": 2,
    "financial_considerations": 1,
    "noise_tolerance": 2,
    "experience": 2,
    "time_commitment": 1,
}

# Function to calculate compatibility score
def calculate_compatibility(user_preferences, pet_characteristics):
    compatibility_score = 0

    if not isinstance(user_preferences, dict) or not isinstance(pet_characteristics, dict):
        raise ValueError("Both user_preferences and pet_characteristics must be dictionaries.")

    for characteristic, weight in WEIGHTS.items():
        user_preference = user_preferences.get(characteristic)
        pet_value = pet_characteristics.get(characteristic)

        if user_preference is not None and user_preference == pet_value:
            compatibility_score += weight

    return compatibility_score


# Compatibility route
@app.route('/compatibility', methods=['GET', 'POST'])
def compatibility():
    if request.method == 'POST':
        user_preferences = {
            "personality": request.form.get("personality"),
            "breed_preference": request.form.get("breed_preference"),
            "pet_parenting": request.form.get("pet_parenting"),
            "climate_zone": request.form.get("climate_zone"),
            "dog_space": request.form.get("dog_space"),
            "allergic_to_hair": request.form.get("allergic_to_hair"),
            "aggressive_friendly": request.form.get("aggressive_friendly"),
            "financial_considerations": request.form.get("financial_considerations"),
            "noise_tolerance": request.form.get("noise_tolerance"),
            "experience": request.form.get("experience"),
            "time_commitment": request.form.get("time_commitment"),
        }

        compatible_pets = []

        for pet in db.pets_for_sale.find():
            pet_characteristics = pet.get('characteristics', {})
            compatibility_score = calculate_compatibility(user_preferences, pet_characteristics)
            if compatibility_score >= 5:
                compatible_pets.append((pet, compatibility_score))

        # Sort compatible pets by compatibility score in descending order
        compatible_pets.sort(key=lambda x: x[1], reverse=True)

        return render_template('compatibility_results.html', compatible_pets=compatible_pets)

    return render_template('compatibility.html')



# Route to post a pet for adoption
@app.route('/post_for_adoption', methods=['GET', 'POST'])
def post_for_adoption():
    if request.method == 'POST':
        name = request.form['name']
        species = request.form['species']
        age = request.form['age']
        characteristics = request.form['characteristics']
        monthlyspent=request.form['monthlyspent']
        contact=request.form['contact']

        # Handle file upload
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

        pet_for_adoption = {
            'name': name,
            'species': species,
            'age': age,
            'characteristics': characteristics,
            'monthlyspent': monthlyspent,
            'contact':contact,
            'image': filename,
        }

        db.pets_for_adoption.insert_one(pet_for_adoption)  # Use 'pets_for_adoption' collection
        return redirect(url_for('view_pets_for_adoption'))

    return render_template('post_for_adoption.html')

# Route to view all pets available for adoption
@app.route('/view_pets_for_adoption')
def view_pets_for_adoption():
    pets_for_adoption = db.pets_for_adoption.find()
    return render_template('view_pets_for_adoption.html', pets_for_adoption=pets_for_adoption)




@app.route('/post_event', methods=['GET', 'POST'])
def post_event():
    if request.method == 'POST':
        event_name = request.form['event_name']
        description = request.form['description']
        date = request.form['date']
        time = request.form['time']
        locality = request.form['locality']

        # Handle file upload for event image
        event_image = request.files['event_image']
        if event_image:
            filename = secure_filename(event_image.filename)
            event_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None

        event = {
            'event_name': event_name,
            'description': description,
            'date': date,
            'time': time,
            'locality': locality,
            'image': filename,
        }

        db.pet_events.insert_one(event)  # Use 'pet_events' collection
        return redirect(url_for('view_events'))

    return render_template('post_event.html')



@app.route('/view_events')
def view_events():
    locality = request.args.get('locality')
    if locality:
        events = db.pet_events.find({'locality': locality})
    else:
        events = db.pet_events.find()

    return render_template('view_events.html', events=events)

# ...

pet_care_responses = {
    "What should I feed my dog?": "You should feed your dog a balanced diet with high-quality dog food. Consult your veterinarian for specific recommendations.",
    "How much exercise does my cat need?": "Cats need daily exercise to stay healthy and active. Play with interactive toys or engage in interactive play sessions to keep them active.",
    "How can I groom my pet at home?": "Grooming your pet at home may include brushing their fur, trimming their nails, and cleaning their ears. Use pet-specific grooming tools and follow online tutorials for guidance.",
    "What vaccinations does my puppy need?": "Puppies need core vaccinations, including distemper, parvovirus, and adenovirus. Consult your vet for a vaccination schedule.",
    "How often should I clean my pet's living space?": "Regular cleaning of your pet's living space is crucial. Clean litter boxes, cages, and habitats as needed to maintain a healthy environment.",
    "How do I train my pet to obey commands?": "Positive reinforcement training is effective for teaching pets commands. Use treats and praise to reward good behavior.",
    "What's the best way to introduce a new pet to the household?": "Introduce new pets gradually and supervise their interactions. Keep them in separate areas initially and use scent swapping to acclimate them to each other's presence.",
    "How do I handle pet emergencies?": "In case of a pet emergency, contact your veterinarian or an emergency pet clinic immediately. Have a first-aid kit and your pet's medical records ready.",
    "How often should I bathe my pet?": "The frequency of bathing depends on your pet's breed and activity level. Many pets need bathing only when they get dirty or start to smell.",
    "What are common signs of pet illness?": "Common signs of illness in pets include changes in appetite, energy levels, vomiting, diarrhea, and difficulty breathing. If you notice these signs, consult your vet.",
    "What's the best way to keep my pet's teeth clean?": "Maintaining good oral health in pets involves brushing their teeth regularly, providing dental chews or toys, and scheduling professional dental cleanings with your vet.",
    "How can I help my overweight pet lose weight?": "Help your overweight pet lose weight by feeding them a controlled diet, increasing exercise, and avoiding high-calorie treats.",
    "What's the ideal temperature for pet comfort?": "Most pets are comfortable at temperatures similar to humans, around 68-72°F (20-22°C). Be aware of temperature extremes.",
    "How do I prevent pet fleas and ticks?": "Prevent fleas and ticks by using vet-recommended flea and tick preventatives and maintaining a clean living environment.",
    "What's the importance of spaying or neutering pets?": "Spaying or neutering your pets helps control the pet population and reduces the risk of certain health issues.",
    "How do I choose the right pet food?": "Select pet food that meets your pet's specific needs, considering factors like age, breed, and any dietary restrictions. Consult your vet for guidance.",
    "What's the best litter for a cat's litter box?": "Choose a cat litter that your cat is comfortable with. Options include clumping, non-clumping, and natural litters.",
    "How do I manage pet allergies?": "If you or someone in your household has pet allergies, consider hypoallergenic breeds, frequent cleaning, and using air purifiers.",
    "How often should I change my pet's water?": "Change your pet's water daily to ensure freshness. Clean the water bowl regularly.",
    "What's the best way to handle pet anxiety?": "For pet anxiety, provide a safe and quiet space, consider behavior modification training, and consult your vet about anti-anxiety medications.",
    "How do I choose the right pet crate or carrier?": "Choose a crate or carrier that provides enough space for your pet to stand, turn, and lie down comfortably during travel or confinement.",
    "How do I stop my pet from scratching furniture?": "To prevent furniture scratching, provide scratching posts, use deterrents, and trim your pet's nails regularly.",
    "How can I tell if my pet is in pain?": "Signs of pet pain may include changes in behavior, limping, restlessness, or whining. Consult your vet if you suspect pain.",
    "What's the importance of microchipping pets?": "Microchipping helps identify and reunite lost pets with their owners. It's a permanent form of identification.",
    "How can I keep my pet safe during extreme weather?": "Protect your pet from extreme weather conditions with appropriate shelter, clothing, and hydration.",
    "What should I do if my pet is constipated?": "If your pet is constipated, consult your vet for advice on dietary changes and possible treatments.",
    "How can I prevent pet dental issues?": "Prevent dental issues by regularly brushing your pet's teeth, providing dental treats, and scheduling professional dental cleanings.",
    "How can I discourage my pet from chewing on household items?": "Use pet-safe chew toys, bitter sprays, and positive reinforcement training to discourage chewing on household items.",
    "How do I help my pet recover from surgery?": "Follow your vet's post-surgery care instructions, keep your pet calm, and provide any prescribed medications.",
    "What's the best way to prepare for a new pet's arrival?": "Prepare for a new pet by pet-proofing your home, gathering supplies, and creating a comfortable space for them.",
    "How do I prevent heatstroke in pets?": "Prevent heatstroke by avoiding hot weather walks, providing shade and hydration, and never leaving your pet in a hot car.",
    "How do I travel with my pet safely?": "Travel with your pet safely by using a secure carrier or restraint and bringing necessary supplies for the journey.",
    "What's the best way to clip my pet's nails?": "Use pet-specific nail clippers, avoid cutting too close to the quick, and reward your pet for good behavior during nail trims.",
    "How can I help my pet cope with loud noises like fireworks?": "Create a quiet, safe space for your pet, play calming music, and use anxiety-reducing products during noisy events.",
    "How often should I take my pet to the veterinarian?": "Regular vet check-ups are typically scheduled annually, but consult your vet for specific recommendations based on your pet's age and health.",
    "What's the best way to introduce my pet to children?": "Introduce pets to children gradually, teach kids how to handle pets gently, and supervise their interactions.",
    "How can I help my senior pet stay comfortable and healthy?": "Provide a comfortable environment, adjust their diet, and schedule regular vet check-ups for senior pets.",
    "How do I prevent pet obesity?": "Prevent obesity by controlling portion sizes, encouraging exercise, and avoiding excessive treats.",
    "What are the signs of pet dental problems?": "Signs of dental problems may include bad breath, difficulty eating, and visible tartar buildup on teeth. Consult your vet for dental care.",
    "How can I create a stimulating environment for my pet?": "Stimulate your pet's mind with interactive toys, puzzle feeders, and regular playtime.",
    "How do I find a pet-friendly rental property?": "Look for pet-friendly listings, provide references, and demonstrate responsible pet ownership when seeking rental properties.",
    "How can I keep my pet safe during car travel?": "Use pet seat belts, carriers, or crates, and make sure your pet is secure and comfortable during car trips.",
    "What's the best way to litter train a kitten?": "Litter train kittens by providing a clean litter box, placing them in it after meals, and praising them for using it.",
    "How do I prevent pet heartworm?": "Prevent heartworm by using heartworm preventatives as prescribed by your vet and keeping your pet away from infected mosquitoes.",
    "How can I address pet separation anxiety?": "To manage separation anxiety, create a predictable routine, use desensitization training, and consult your vet for advice.",
    "What's the best way to provide enrichment for pets?": "Enrich your pet's life with interactive toys, puzzle feeders, and rotating their toys to prevent boredom.",
    "How do I choose a pet insurance plan?": "Choose a pet insurance plan that covers your pet's specific needs and fits your budget. Review terms, coverage, and exclusions carefully.",
    "What's the best way to clean pet stains and odors?": "Clean pet stains and odors with pet-specific enzymatic cleaners to eliminate odors and deter repeat accidents.",
    "How can I help my pet cope with thunderstorms?": "Provide a safe and comfortable space, play calming music, and use anxiety-reducing products during thunderstorms.",
    "What's the importance of regular pet exercise?": "Regular exercise is crucial for a pet's physical and mental well-being. It helps maintain a healthy weight and reduces behavioral issues.",
    "How do I introduce my pet to a new baby?": "Prepare your pet for a new baby by gradually adjusting to changes, maintaining routines, and supervising interactions.",
    "How can I find a reputable pet trainer?": "Research and choose a pet trainer with positive reviews, certifications, and a training approach that aligns with your goals and values.",
    "What's the best way to maintain a pet's coat health?": "Maintain your pet's coat by regular brushing, feeding a balanced diet, and using appropriate grooming products.",
    "How do I choose a safe pet collar or harness?": "Select a collar or harness that fits your pet comfortably, provides proper identification, and allows for safe walks.",
    "How can I provide mental stimulation for my pet?": "Mentally stimulate your pet with puzzle toys, training sessions, and introducing new experiences.",
    "What's the best way to prevent pet allergies in the home?": "Prevent pet allergies by regularly cleaning, using allergen-resistant covers, and maintaining good indoor air quality.",
    "How do I protect my pet from poisonous plants and substances?": "Identify and remove poisonous plants and substances from your home and yard to protect your pet.",
    "How can I teach my pet to walk on a leash?": "Teach your pet to walk on a leash by using positive reinforcement, treats, and gradual training in a quiet environment.",
    "What's the importance of regular pet check-ups?": "Regular vet check-ups are essential for early disease detection and maintaining your pet's overall health.",
    "How do I socialize my pet with other animals?": "Socialize your pet with other animals by exposing them to different experiences and providing positive interactions.",
    "How can I keep my pet's ears clean and healthy?": "Clean your pet's ears gently and regularly using vet-recommended ear cleaning solutions.",
    "What's the best way to handle a pet with separation anxiety?": "Managing separation anxiety involves creating a predictable routine and gradually increasing the time your pet spends alone.",
    "How do I find a missing pet?": "To find a missing pet, distribute flyers, check local shelters, and use online resources and social media.",
    "How can I prepare my pet for travel by air?": "Prepare your pet for air travel by following airline guidelines, using an appropriate carrier, and practicing crate training.",
    "What's the importance of socializing a puppy?": "Socializing a puppy helps them adapt to various people, animals, and environments, reducing the risk of behavior issues later in life.",
    "How do I choose the right pet bed?": "Select a comfortable and appropriately sized pet bed that suits your pet's sleeping style.",
    "How can I help my pet adapt to a new home?": "Help your pet adapt to a new home by maintaining routines, providing a familiar environment, and offering comfort and reassurance.",
    "What's the best way to discourage pet digging behavior?": "Discourage digging by creating a designated digging area, keeping your pet engaged, and using deterrents in areas where digging is not allowed.",
    "How do I prevent pet aggression towards other pets?": "Prevent pet aggression through positive reinforcement training, behavior modification, and supervision during interactions with other pets.",
    "How can I protect my pet from common household hazards?": "Secure hazardous items, use childproof latches, and pet-proof your home to protect your pet from common household dangers.",
    "What's the importance of pet identification tags?": "Pet ID tags help identify your pet in case they get lost. Include your contact information and any medical needs on the tag.",
    "How can I keep my pet entertained while I'm at work?": "Entertain your pet while you're at work by providing interactive toys, puzzle feeders, and safe spaces for them to play.",
    "How do I handle pet aggression towards humans?": "Address pet aggression towards humans through professional behavior training and avoiding triggers for aggressive behavior.",
    "How can I prepare my pet for visits to the vet?": "Prepare your pet for vet visits by acclimating them to the carrier, rewarding them for calm behavior, and maintaining a positive association with vet visits.",
    "What's the best way to help a pet with arthritis?": "Help pets with arthritis by providing joint supplements, gentle exercise, and cozy resting spots.",
    "How do I prevent and manage pet hair shedding?": "Prevent and manage pet hair shedding by regular grooming, using deshedding tools, and maintaining a clean home.",
    "How can I provide mental enrichment for indoor pets?": "Indoor pets benefit from mental enrichment through interactive toys, puzzle feeders, and safe outdoor experiences.",
    "What's the importance of proper pet nutrition?": "Proper nutrition is essential for your pet's health. Consult your vet for dietary recommendations based on your pet's age, breed, and health conditions.",
    "How do I help my pet cope with moving to a new home?": "Help your pet adjust to a new home by keeping them in a quiet space during the move, providing familiar items, and gradually introducing them to the new environment.",
    "How can I stop my pet from scratching themselves excessively?": "Consult your vet to determine the cause of excessive scratching and follow their recommended treatment plan to alleviate discomfort.",
    "What's the importance of flea and tick prevention for pets?": "Flea and tick prevention is crucial to protect your pet from diseases and discomfort. Use vet-recommended preventatives as directed.",
    "How do I introduce my pet to water and swimming?": "Gradually introduce your pet to water and swimming, providing positive experiences and using appropriate safety measures.",
    "How can I keep my pet's eyes clean and healthy?": "Maintain your pet's eye health by gently cleaning around their eyes as needed and consulting your vet if you notice discharge or irritation.",
    "What's the best way to transport small pets securely in a car?": "Use a secure pet carrier or restraint to transport small pets in a car. Ensure proper ventilation and comfort during the journey.",
    "How do I help my pet adjust to a new addition to the family?": "Help your pet adjust to a new family member by maintaining routines, providing positive associations, and allowing gradual interactions.",
    "How can I provide a balanced diet for my pet?": "Consult your vet to create a balanced diet that meets your pet's specific needs, considering age, breed, and dietary restrictions.",
    "What's the importance of providing mental stimulation for pets?": "Mental stimulation prevents boredom and encourages healthy behavior. Use puzzles, interactive toys, and training sessions to engage your pet's mind.",
    "How do I protect my pet from toxic plants and substances in the garden?": "Identify and remove toxic plants and substances from your garden to keep your pet safe from harm.",
    "How can I help my pet overcome fear of thunderstorms and fireworks?": "Comfort your pet during thunderstorms and fireworks with a safe space, calming music, and anxiety-reducing products.",
    "What's the importance of socialization for puppies?": "Socialization is critical for puppies to develop good behavior and adapt to new environments and experiences.",
    "How do I provide enrichment for pets in a small living space?": "Even in a small living space, you can provide pet enrichment through interactive toys, vertical space, and daily playtime.",
    "How can I help my pet cope with grief and loss?": "Provide extra love and comfort to your pet during times of grief and loss. Keep routines stable and offer support.",
    "What's the importance of pet dental care?": "Dental care is vital to prevent dental disease and maintain your pet's overall health. Brush your pet's teeth and consult your vet for dental check-ups.",
    "How do I train my pet to walk nicely on a leash?": "Train your pet to walk nicely on a leash with positive reinforcement, practice, and consistency.",
    "How can I protect my pet from common outdoor hazards?": "Supervise outdoor activities, use a leash or harness, and prevent access to toxic plants and substances to protect your pet from common outdoor hazards.",
    "What's the importance of regular flea and tick prevention?": "Regular flea and tick prevention is essential to protect your pet from infestations, diseases, and discomfort.",
    "How do I prepare my pet for a long car trip?": "Prepare your pet for a long car trip by acclimating them to the car, using a secure carrier or restraint, and scheduling rest breaks.",
    "How can I address pet resource guarding behavior?": "Address resource guarding behavior through positive training, using trade-ups, and seeking guidance from a professional trainer.",
    "What's the importance of pet exercise for mental health?": "Regular exercise is crucial for your pet's mental well-being. It reduces stress, anxiety, and boredom.",
    "How do I help my pet overcome a fear of water?": "Help your pet overcome a fear of water with gradual introductions and positive associations with water-related experiences.",
    "How can I make vet visits less stressful for my pet?": "Make vet visits less stressful by acclimating your pet to the carrier, providing comfort items, and using positive reinforcement during the visit.",
    "What's the importance of a consistent routine for pets?": "A consistent routine helps pets feel secure and comfortable. It includes feeding, playtime, and bedtime schedules.",
    "How do I choose the right toys for my pet?": "Choose toys appropriate for your pet's size and activity level. Avoid small, easily swallowed items.",
    "How can I prevent pet dehydration during hot weather?": "Prevent pet dehydration by providing fresh water, shade, and shorter outdoor playtimes during hot weather.",
    "How to help my pet recover from surgery?": "Follow your vet's post-surgery care instructions, provide a quiet recovery space, and administer prescribed medications as directed.",
    "How can I prepare my pet for social interactions with other pets?": "Prepare your pet for social interactions by gradually introducing them to other pets, monitoring behavior, and using positive reinforcement.",
    "What's the importance of pet playtime and exercise?": "Playtime and exercise are crucial for a pet's physical health, mental stimulation, and bonding with their owner.",
    "How do I prevent pet anxiety during car travel?": "Prevent pet anxiety during car travel by using a secure carrier, practicing short trips, and offering rewards for calm behavior.",
}




if __name__ == '__main__':
    app.run(debug=True)


