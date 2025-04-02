import wikipedia
import pickle
import re
from tqdm import tqdm

def scrape_data(query, n):
    return wikipedia.search(query, results = n)

def remove_duplicates(documents):
    for i in tqdm(range(len(documents)), desc = "Removing Duplicates"):
        for page in documents[i]:
            for j in range(len(documents)):
                if i == j:
                    continue
                if page in documents[j]:
                    documents[j].remove(page)
    return documents

def getnumDocs(documents):
    for document in documents:
        # assert len(document) == 600, f"Length is {len(document)}, not 600."
        print(f"Number of documents per topic: {len(document)}")

def removeShortSummaries(documents):
    for document in documents:
        for page in tqdm(document.copy(), desc = "Removing short and error summaries"):
            try:
                content = wikipedia.page(page, auto_suggest = False)
                summary = content.summary
                if len(summary) < 200:
                    document.remove(page)
            except:
                document.remove(page)
                
        
    return documents

def pickleDocs(documents):
    with open("documents.pkl", "wb") as f:
        pickle.dump(documents, f)
        
def loadDocs(documents_file):
    with open(documents_file, "rb") as file:
        documents = pickle.load(file)
    return documents

def filter_summary(summary):
    regex = r"[^a-zA-Z0-9 ]+"
    whitespace_regex = r"[ ]+"
    
    new_summary = re.sub(regex, " ", summary)
    new_summary = re.sub(whitespace_regex, " ", new_summary)
    return new_summary

def preprocessAll(documents):
    data = { "Health": [], "Environment": [], "Technology": [], "Economy": [],
        "Entertainment": [], "Sports": [], "Politics": [], "Education": [],
        "Travel": [], "Food": []
        }

    topics = ["Health", "Environment", "Technology", "Economy", "Entertainment", "Sports", "Politics", "Education", "Travel", "Food"]

    topic_counter = 0

    for document in tqdm(documents, desc = "Preprocessing..."):
        for page in document.copy():
            try:
                page_content = {}
                content = wikipedia.page(page, auto_suggest = False)
                revision_id = content.revision_id
                title = content.title
                summary = content.summary
                summary = filter_summary(summary)
                url = content.url
                topic = topics[topic_counter]
                
                page_content["revision_id"] = str(revision_id)
                page_content["title"] = str(title)
                page_content["summary"] = str(summary)
                page_content["url"] = str(url)
                page_content["topic"] = str(topic)
                
                data[topic].append(page_content)
            except: # if the page throws an error 
                document.remove(page)
                
        topic_counter += 1
            
        
    with open("p3_preprocessed_documents.pkl2", "wb") as f:
        pickle.dump(data, f)



def main():
    print("Starting scraping")
    health_results = (wikipedia.search("Global Health Statistics", results=500) + wikipedia.search("Common Diseases", results=500) + 
    wikipedia.search("Mental Health Trends", results=500) + wikipedia.search("COVID", results=500) + wikipedia.search("Flu Statistics", results=500)
    + wikipedia.search("Autism", results=500) + wikipedia.search("Diabetes Statistics", results=500) + wikipedia.search("Common Cold Statistics", results=500)
    + wikipedia.search("Listeria Statistics", results=500) + wikipedia.search("Obesity Rates", results=500) + wikipedia.search("Quarantine", results=500)
    + wikipedia.search("Mad Cow Disease", results=500) + wikipedia.search("Ebola", results=500) + wikipedia.search("HIV", results=500))
    
    environment_results = (wikipedia.search("Global Warming", results=500) + wikipedia.search("Endangered Species", results=500) 
    + wikipedia.search("Deforestation Rates", results=500)  + wikipedia.search("Endangered Dolphins", results=500)
    + wikipedia.search("Ozone Layer Depletion", results=500) + wikipedia.search("Forest Fires", results=500)
    + wikipedia.search("Pollution", results=500) + wikipedia.search("CO2 Emissions", results=500) + wikipedia.search("Greenhouse Gases", results=500)
    + wikipedia.search("Fossil Fuel Dangers", results=500) + wikipedia.search("Is Solar Power Good for the Environment?", results=500)
    + wikipedia.search("Glacier Melting", results=500) + wikipedia.search("Climate Change", results=500) + wikipedia.search("Tornado Chances in New York", results=500)
    + wikipedia.search("Different Climates In Japan", results=500) + wikipedia.search("Different Climates In Korea", results=500) + wikipedia.search("Alternatives To Fossil Fuels", results=500)
    + wikipedia.search("Environment Statistics", results=500) + wikipedia.search("Different Types of Environments", results=500))
    
    technology_results = (wikipedia.search("AI Advancements", results=500) + wikipedia.search("Emerging Technologies", results=500) + wikipedia.search("GPU Costs", results=500)
    + wikipedia.search("Microprocessor Advancements", results=500) + wikipedia.search("LLMs", results=500) + wikipedia.search("ChatGPT", results=500) + wikipedia.search("Generative AI", results=500)
    + wikipedia.search("Software", results=500) + wikipedia.search("Distributed Systems", results=500) + wikipedia.search("Blockchain", results=500) + wikipedia.search("NFTs", results=500)
    + wikipedia.search("AI in Cars", results=500) + wikipedia.search("Computer Vision Advancements", results=500) + wikipedia.search("Deep Fake Technology", results=500)
    + wikipedia.search("Machine Learning Applications", results=500) + wikipedia.search("Deep Learning Applications", results=500) + wikipedia.search("Advancements In Medical Technology", results=500))
    
    economy_results = (wikipedia.search("Stock Market Performance", results=500) + wikipedia.search("Nursing Job Market", results=500) + wikipedia.search("Cryptocurrency Trends", results=500)
    + wikipedia.search("Software Engineering Job Market", results=500) + wikipedia.search("Stock Market Crash", results=500) + wikipedia.search("Economy", results=500) 
    + wikipedia.search("Bitcoin", results=500) + wikipedia.search("Supply and Demand", results=500) + wikipedia.search("GDP", results=500) + wikipedia.search("Consumer Price Index", results=500)
    + wikipedia.search("Inflation", results=500) + wikipedia.search("Imports and Exports", results=500) + wikipedia.search("Value of the US Dollar Trends", results=500) + wikipedia.search("Value of the Japanese Yen Trends", results=500)
    + wikipedia.search("Medical Job Market", results=500) + wikipedia.search("Accounting Job Market", results=500) + wikipedia.search("IT Job Market", results=500) + wikipedia.search("Carpenter Job Market", results=500))
    
    entertainment_results = (wikipedia.search("Music Industry", results=500) + wikipedia.search("Popular Cultural Events", results=500) + wikipedia.search("Streaming Platforms", results=500)
    + wikipedia.search("Rap Industry", results=500) + wikipedia.search("Country Music", results=500) + wikipedia.search("Netflix Comedies", results=500)
    + wikipedia.search("Youtube Top Videos", results=500) + wikipedia.search("Popular Comedy Shows", results=500) + wikipedia.search("Popular Horror Films", results=500)
    + wikipedia.search("Popular Action Films", results=500) + wikipedia.search("Top Japanese Music", results=500) + wikipedia.search("Top K-POP Music", results=500)
    + wikipedia.search("Rock Music Industry", results=500) + wikipedia.search("Soul Music Industry", results=500) + wikipedia.search("Top Russian Shows", results=500))
    
    sports_results = (wikipedia.search("Major sporting events", results=500) + wikipedia.search("Superbowl", results=500) + wikipedia.search("Sports Analytics", results=500)
    + wikipedia.search("Basketball Leagues", results=500) + wikipedia.search("Basketball Leagues", results=500) + wikipedia.search("Baseball Leagues", results=500)
    + wikipedia.search("Soccer Leagues", results=500) + wikipedia.search("Football Leagues", results=500) + wikipedia.search("European Sports", results=500)
    + wikipedia.search("Japanese Baseball vs American Baseball", results=500) + wikipedia.search("Pickleball", results=500) + wikipedia.search("Tennis", results=500)
    + wikipedia.search("Handball Leagues", results=500) + wikipedia.search("Women's Basketball League", results=500) + wikipedia.search("Top China Basketball Teams", results=500)
    + wikipedia.search("Top Bowling Players", results=500) + wikipedia.search("Voleyball Leagues", results=500) + wikipedia.search("Top Snowboarding Athletes", results=500))
    
    politics_results = (wikipedia.search("Elections", results=500) + wikipedia.search("Public Policy Analysis", results=500) + wikipedia.search("Presidential Debate", results=500)
    + wikipedia.search("Democracy", results=500) + wikipedia.search("Dictatorship", results=500) + wikipedia.search("Communism", results=500) + wikipedia.search("Federalism", results=500)
    + wikipedia.search("Capitalism", results=500) + wikipedia.search("Human Rights", results=500) + wikipedia.search("Barack Obama", results=500) + wikipedia.search("Joe Biden", results=500)
    + wikipedia.search("Imperialism", results=500) + wikipedia.search("Women's Suffrage", results=500))
    
    education_results = (wikipedia.search("Student Loan Data", results=500) + wikipedia.search("Literacy Rates", results=500) + wikipedia.search("College Dropout Rates", results=500)
    + wikipedia.search("College Graduation Rates", results=500) + wikipedia.search("Top Colleges Globally", results=500) + wikipedia.search("Standardized Testing", results=500)
    + wikipedia.search("SAT", results=500) + wikipedia.search("ACT", results=500) + wikipedia.search("Teacher Unions", results=500) + wikipedia.search("Private Education", results=500)
    + wikipedia.search("Charter Schools", results=500) + wikipedia.search("Home Schooling", results=500) + wikipedia.search("American Education System vs. European Education System", results=500)
    + wikipedia.search("European Education System vs. Asian Education System", results=500) + wikipedia.search("Most Expensive Colleges", results=500)+ wikipedia.search("Cheapest Colleges", results=500)
    + wikipedia.search("Top Ranked College Majors in The US", results=500) + wikipedia.search("Best Computer Science Programs Globally", results=500) + wikipedia.search("Best Nursing Programs Globally", results=500))
    
    travel_results = (wikipedia.search("Travel Trends", results=500) + wikipedia.search("Top Tourist Destinations", results=500) + wikipedia.search("Most Popular Airports", results=500)
    + wikipedia.search("Japan Travel Trends", results=500) + wikipedia.search("China Tourism", results=500) + wikipedia.search("India Tourism", results=500)
    + wikipedia.search("Cheapest Airlines", results=500) + wikipedia.search("Expensive Airlines", results=500) + wikipedia.search("Is Spirit A Good Airline?", results=500)
    + wikipedia.search("Airport Lounges", results=500) + wikipedia.search("Business Class Benefits", results=500) + wikipedia.search("Delta vs American Airlines", results=500)
    + wikipedia.search("Should I Fly United Airlines?", results=500) + wikipedia.search("Connecting Flights to Japan", results=500) + wikipedia.search("Top Places To Visit in Europe", results=500) + wikipedia.search("Top Places To Visit in Africa", results=500)
    + wikipedia.search("Top Places To Visit in India", results=500) + wikipedia.search("Top Places To Visit in China", results=500) + wikipedia.search("Top Places To Visit in Greece", results=500))
    
    food_results = (wikipedia.search("Crop yield statistics", results=500) + wikipedia.search("Global Hunger", results=500) + wikipedia.search("Food Security", results=500)
    + wikipedia.search("Food Security in the US", results=500) + wikipedia.search("Top Ranked Foods", results=500) + wikipedia.search("Top Foods in China", results=500)
    + wikipedia.search("Top Foods in Japan", results=500) + wikipedia.search("Top Foods in India", results=500) + wikipedia.search("Top Foods in the US", results=500)
    + wikipedia.search("Top Foods Globally", results=500) + wikipedia.search("Most Expensive Foods", results=500) + wikipedia.search("Worst Foods in the US", results=500)
    + wikipedia.search("Top Unsafe Foods", results=500) + wikipedia.search("Top Desserts in the World", results=500) + wikipedia.search("Top African Foods", results=500) + wikipedia.search("Top Korean Foods", results=500)
    + wikipedia.search("Amount of Beef Eaten in the US", results=500) + wikipedia.search("Amount of Beef Eaten in Japan", results=500) + wikipedia.search("Plant-Based Diet vs. Animal-Based Diet", results=500) + wikipedia.search("Most Nutrient Dense Foods", results=500)
    + wikipedia.search("Food Waste in 2023", results=500) + wikipedia.search("GMOs in Foods", results=500) + wikipedia.search("Where to Get The Sweetest Mangos", results=500))
    

    print("finshed scraping")
    documents = [set(health_results), set(environment_results), set(technology_results), set(economy_results), set(entertainment_results), set(sports_results), set(politics_results), set(education_results), set(travel_results), set(food_results)]
    
    print("num docs after scraping")
    getnumDocs(documents)
    
    documents = remove_duplicates(documents)
    print("num docs after removing duplicates")
    getnumDocs(documents)
    
    with open("docs_after_removing_duplicates2.pkl", "wb") as f:
        pickle.dump(documents, f)
        
    documents = removeShortSummaries(documents)
    print("num docs after removing short and error summaries")
    getnumDocs(documents)
    
    with open("docs_before_preprocess.pkl2", "wb") as f:
        pickle.dump(documents, f)
    
    final_documents = preprocessAll(documents)
    
    
    
    
    print("done finalizing documents after preprocessing")
    print("\n final num docs")
    getnumDocs(documents)
    
    
    return final_documents
    
    

if __name__ == "__main__":
    main()