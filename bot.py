import logging
import random
import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database of 200 celebrities
CELEBRITIES = [
    {"name": "Mohamed Salah", "country": "Egypt", "category": "Sports", "emoji": "⚽", "description": "Egyptian and global football legend"},
    {"name": "Amr Diab", "country": "Egypt", "category": "Singer", "emoji": "🎤", "description": "King of Arabic pop music"},
    {"name": "Leonardo DiCaprio", "country": "USA", "category": "Actor", "emoji": "🎬", "description": "Hollywood superstar and Oscar winner"},
    {"name": "Nawal El Zoghbi", "country": "Lebanon", "category": "Singer", "emoji": "🎶", "description": "Lebanese singer with golden voice"},
    {"name": "Mohamed Henedy", "country": "Egypt", "category": "Comedian", "emoji": "😂", "description": "Egyptian comedy superstar"},
    {"name": "Tom Cruise", "country": "USA", "category": "Actor", "emoji": "🕴️", "description": "Action movie legend"},
    {"name": "Shakira", "country": "Colombia", "category": "Singer", "emoji": "💃", "description": "Hips don't lie!"},
    {"name": "Cristiano Ronaldo", "country": "Portugal", "category": "Sports", "emoji": "🔥", "description": "Football GOAT contender"},
    {"name": "Fairuz", "country": "Lebanon", "category": "Singer", "emoji": "🎵", "description": "Arab world's most famous singer"},
    {"name": "Adel Imam", "country": "Egypt", "category": "Actor", "emoji": "🎭", "description": "Egypt's comedy genius"},
    {"name": "Will Smith", "country": "USA", "category": "Actor", "emoji": "😎", "description": "Fresh Prince turned superstar"},
    {"name": "Beyoncé", "country": "USA", "category": "Singer", "emoji": "👑", "description": "Queen Bey of pop music"},
    {"name": "The Rock", "country": "USA", "category": "Actor", "emoji": "💪", "description": "Wrestler turned Hollywood star"},
    {"name": "Taylor Swift", "country": "USA", "category": "Singer", "emoji": "🎸", "description": "Pop music phenomenon"},
    {"name": "Brad Pitt", "country": "USA", "category": "Actor", "emoji": "🎥", "description": "Hollywood heartthrob"},
    {"name": "Angelina Jolie", "country": "USA", "category": "Actress", "emoji": "❤️", "description": "Actress and humanitarian"},
    {"name": "Robert Downey Jr.", "country": "USA", "category": "Actor", "emoji": "🤖", "description": "Iron Man himself"},
    {"name": "Johnny Depp", "country": "USA", "category": "Actor", "emoji": "🏴‍☠️", "description": "Pirate captain extraordinaire"},
    {"name": "Morgan Freeman", "country": "USA", "category": "Actor", "emoji": "🎙️", "description": "Voice of God"},
    {"name": "Emma Watson", "country": "UK", "category": "Actress", "emoji": "📚", "description": "Hermione Granger in real life"},
    {"name": "Dwayne Johnson", "country": "USA", "category": "Actor", "emoji": "💎", "description": "Can you smell what The Rock is cooking?"},
    {"name": "Jennifer Lopez", "country": "USA", "category": "Singer", "emoji": "💎", "description": "Jenny from the block!"},
    {"name": "Chris Hemsworth", "country": "Australia", "category": "Actor", "emoji": "🔨", "description": "Thor's hammer awaits!"},
    {"name": "Scarlett Johansson", "country": "USA", "category": "Actress", "emoji": "🕷️", "description": "Black Widow energy!"},
    {"name": "Keanu Reeves", "country": "Canada", "category": "Actor", "emoji": "🚗", "description": "John Wick mode activated!"},
    {"name": "Lionel Messi", "country": "Argentina", "category": "Sports", "emoji": "🥅", "description": "Football magician"},
    {"name": "Kylian Mbappé", "country": "France", "category": "Sports", "emoji": "⚡", "description": "Speed demon of football"},
    {"name": "Neymar Jr.", "country": "Brazil", "category": "Sports", "emoji": "🎯", "description": "Brazilian dribbling wizard"},
    {"name": "Zendaya", "country": "USA", "category": "Actress", "emoji": "🌟", "description": "Euphoria star"},
    {"name": "Timothée Chalamet", "country": "USA", "category": "Actor", "emoji": "🎨", "description": "Hollywood's young talent"},
    {"name": "Harry Styles", "country": "UK", "category": "Singer", "emoji": "🌸", "description": "Former One Direction star"},
    {"name": "Ariana Grande", "country": "USA", "category": "Singer", "emoji": "🍭", "description": "Pop princess"},
    {"name": "Drake", "country": "Canada", "category": "Singer", "emoji": "🦉", "description": "Rap superstar"},
    {"name": "Post Malone", "country": "USA", "category": "Singer", "emoji": "🍺", "description": "Tattooed music star"},
    {"name": "Billie Eilish", "country": "USA", "category": "Singer", "emoji": "🖤", "description": "Alternative pop sensation"},
    {"name": "The Weeknd", "country": "Canada", "category": "Singer", "emoji": "🌃", "description": "R&B superstar"},
    {"name": "Ed Sheeran", "country": "UK", "category": "Singer", "emoji": "➕", "description": "Ginger singing sensation"},
    {"name": "Bruno Mars", "country": "USA", "category": "Singer", "emoji": "🕺", "description": "Funk and pop master"},
    {"name": "Lady Gaga", "country": "USA", "category": "Singer", "emoji": "🎭", "description": "Pop icon and actress"},
    {"name": "Eminem", "country": "USA", "category": "Singer", "emoji": "🎤", "description": "Rap god"},
    {"name": "Snoop Dogg", "country": "USA", "category": "Singer", "emoji": "🐕", "description": "Hip-hop legend"},
    {"name": "Kanye West", "country": "USA", "category": "Singer", "emoji": "🎓", "description": "Controversial music genius"},
    {"name": "Rihanna", "country": "Barbados", "category": "Singer", "emoji": "💄", "description": "Billionaire businesswoman"},
    {"name": "Jay-Z", "country": "USA", "category": "Singer", "emoji": "💰", "description": "Hip-hop mogul"},
    {"name": "BTS", "country": "South Korea", "category": "Group", "emoji": "💜", "description": "Global K-pop sensation"},
    {"name": "Blackpink", "country": "South Korea", "category": "Group", "emoji": "🖤💗", "description": "K-pop girl group"},
    {"name": "Tiger Woods", "country": "USA", "category": "Sports", "emoji": "⛳", "description": "Golf legend"},
    {"name": "Serena Williams", "country": "USA", "category": "Sports", "emoji": "🎾", "description": "Tennis queen"},
    {"name": "Usain Bolt", "country": "Jamaica", "category": "Sports", "emoji": "⚡", "description": "Fastest man alive"},
    {"name": "Michael Phelps", "country": "USA", "category": "Sports", "emoji": "🏊", "description": "Olympic swimming legend"},
    {"name": "Conor McGregor", "country": "Ireland", "category": "Sports", "emoji": "🥊", "description": "MMA superstar"},
    {"name": "Mike Tyson", "country": "USA", "category": "Sports", "emoji": "🐯", "description": "Boxing legend"},
    {"name": "Muhammad Ali", "country": "USA", "category": "Sports", "emoji": "🦋", "description": "Greatest boxer ever"},
    {"name": "David Beckham", "country": "UK", "category": "Sports", "emoji": "⚽", "description": "Football icon and model"},
    {"name": "Oprah Winfrey", "country": "USA", "category": "TV", "emoji": "🎁", "description": "Media mogul"},
    {"name": "Ellen DeGeneres", "country": "USA", "category": "TV", "emoji": "💃", "description": "Talk show host"},
    {"name": "Gordon Ramsay", "country": "UK", "category": "TV", "emoji": "👨‍🍳", "description": "Celebrity chef"},
    {"name": "Mr. Bean", "country": "UK", "category": "Actor", "emoji": "🚗", "description": "Silent comedy genius"},
    {"name": "Charlie Chaplin", "country": "UK", "category": "Actor", "emoji": "🎩", "description": "Silent film legend"},
    {"name": "Marilyn Monroe", "country": "USA", "category": "Actress", "emoji": "💋", "description": "Hollywood icon"},
    {"name": "Elvis Presley", "country": "USA", "category": "Singer", "emoji": "🎸", "description": "King of Rock and Roll"},
    {"name": "Michael Jackson", "country": "USA", "category": "Singer", "emoji": "🌙", "description": "King of Pop"},
    {"name": "Freddie Mercury", "country": "UK", "category": "Singer", "emoji": "🎤", "description": "Queen frontman"},
    {"name": "Bob Marley", "country": "Jamaica", "category": "Singer", "emoji": "🍁", "description": "Reggae legend"},
    {"name": "Whitney Houston", "country": "USA", "category": "Singer", "emoji": "🎶", "description": "One of the greatest voices"},
    {"name": "Elon Musk", "country": "USA", "category": "Business", "emoji": "🚀", "description": "Tech billionaire"},
    {"name": "Steve Jobs", "country": "USA", "category": "Business", "emoji": "🍎", "description": "Apple co-founder"},
    {"name": "Mark Zuckerberg", "country": "USA", "category": "Business", "emoji": "👓", "description": "Facebook founder"},
    {"name": "Jeff Bezos", "country": "USA", "category": "Business", "emoji": "📦", "description": "Amazon founder"},
    {"name": "Warren Buffett", "country": "USA", "category": "Business", "emoji": "💰", "description": "Investment legend"},
    {"name": "Tony Stark", "country": "USA", "category": "Fictional", "emoji": "🤖", "description": "Iron Man"},
    {"name": "Sherlock Holmes", "country": "UK", "category": "Fictional", "emoji": "🔍", "description": "Detective genius"},
    {"name": "Harry Potter", "country": "UK", "category": "Fictional", "emoji": "⚡", "description": "The Boy Who Lived"},
    {"name": "Spider-Man", "country": "USA", "category": "Fictional", "emoji": "🕷️", "description": "Friendly neighborhood hero"},
    {"name": "Batman", "country": "USA", "category": "Fictional", "emoji": "🦇", "description": "Dark Knight"},
    {"name": "Superman", "country": "USA", "category": "Fictional", "emoji": "🦸", "description": "Man of Steel"},
    {"name": "Wonder Woman", "country": "USA", "category": "Fictional", "emoji": "🦸‍♀️", "description": "Amazon princess"},
    {"name": "Deadpool", "country": "USA", "category": "Fictional", "emoji": "💀", "description": "Merc with a mouth"},
    {"name": "Wolverine", "country": "Canada", "category": "Fictional", "emoji": "🦾", "description": "X-Men mutant"},
    {"name": "Captain America", "country": "USA", "category": "Fictional", "emoji": "🇺🇸", "description": "Super soldier"},
    {"name": "Thor", "country": "Asgard", "category": "Fictional", "emoji": "⚡", "description": "God of Thunder"},
    {"name": "Hulk", "country": "USA", "category": "Fictional", "emoji": "💚", "description": "Big green monster"},
    {"name": "Black Panther", "country": "Wakanda", "category": "Fictional", "emoji": "🐾", "description": "Wakanda forever!"},
    {"name": "Doctor Strange", "country": "USA", "category": "Fictional", "emoji": "🌀", "description": "Sorcerer Supreme"},
    {"name": "Gandalf", "country": "Middle Earth", "category": "Fictional", "emoji": "🧙", "description": "Wizard"},
    {"name": "Darth Vader", "country": "Galactic Empire", "category": "Fictional", "emoji": "⚫", "description": "Sith Lord"},
    {"name": "Yoda", "country": "Dagobah", "category": "Fictional", "emoji": "👽", "description": "Jedi Master"},
    {"name": "Luke Skywalker", "country": "Tatooine", "category": "Fictional", "emoji": "⚔️", "description": "Jedi Knight"},
    {"name": "Princess Leia", "country": "Alderaan", "category": "Fictional", "emoji": "👑", "description": "Rebel leader"},
    {"name": "Neo", "country": "The Matrix", "category": "Fictional", "emoji": "👓", "description": "The One"},
    {"name": "Morpheus", "country": "The Matrix", "category": "Fictional", "emoji": "🕶️", "description": "Red pill or blue pill?"},
    {"name": "Forrest Gump", "country": "USA", "category": "Fictional", "emoji": "🏃", "description": "Run Forrest run!"},
    {"name": "Titanic Jack", "country": "USA", "category": "Fictional", "emoji": "🚢", "description": "I'm king of the world!"},
    {"name": "James Bond", "country": "UK", "category": "Fictional", "emoji": "🔫", "description": "Secret agent 007"},
    {"name": "Indiana Jones", "country": "USA", "category": "Fictional", "emoji": "🤠", "description": "Archaeologist adventurer"},
    {"name": "Mickey Mouse", "country": "USA", "category": "Cartoon", "emoji": "🐭", "description": "Disney icon"},
    {"name": "Donald Duck", "country": "USA", "category": "Cartoon", "emoji": "🦆", "description": "Angry duck"},
    {"name": "Bugs Bunny", "country": "USA", "category": "Cartoon", "emoji": "🥕", "description": "What's up doc?"},
    {"name": "Scooby-Doo", "country": "USA", "category": "Cartoon", "emoji": "🐕", "description": "Mystery solving dog"},
    {"name": "SpongeBob", "country": "Bikini Bottom", "category": "Cartoon", "emoji": "🧽", "description": "SquarePants"},
    {"name": "Patrick Star", "country": "Bikini Bottom", "category": "Cartoon", "emoji": "⭐", "description": "SpongeBob's best friend"},
    {"name": "Homer Simpson", "country": "USA", "category": "Cartoon", "emoji": "🍩", "description": "D'oh!"},
    {"name": "Bart Simpson", "country": "USA", "category": "Cartoon", "emoji": "🛹", "description": "Underachiever"},
    {"name": "Rick Sanchez", "country": "USA", "category": "Cartoon", "emoji": "🔬", "description": "Mad scientist"},
    {"name": "Morty Smith", "country": "USA", "category": "Cartoon", "emoji": "😰", "description": "Rick's grandson"},
    {"name": "Goku", "country": "Japan", "category": "Anime", "emoji": "🐉", "description": "Saiyan warrior"},
    {"name": "Naruto Uzumaki", "country": "Japan", "category": "Anime", "emoji": "🍜", "description": "Future Hokage"},
    {"name": "Luffy", "country": "Japan", "category": "Anime", "emoji": "🏴‍☠️", "description": "Future Pirate King"},
    {"name": "Pikachu", "country": "Japan", "category": "Anime", "emoji": "⚡", "description": "Electric Pokemon"},
    {"name": "Mario", "country": "Japan", "category": "Game", "emoji": "🍄", "description": "Plumber hero"},
    {"name": "Luigi", "country": "Japan", "category": "Game", "emoji": "👻", "description": "Mario's brother"},
    {"name": "Sonic", "country": "Japan", "category": "Game", "emoji": "🌀", "description": "Fast hedgehog"},
    {"name": "Master Chief", "country": "USA", "category": "Game", "emoji": "🪖", "description": "Halo protagonist"},
    {"name": "Lara Croft", "country": "UK", "category": "Game", "emoji": "🏹", "description": "Tomb Raider"},
    {"name": "Kratos", "country": "Greece", "category": "Game", "emoji": "⚔️", "description": "God of War"},
    {"name": "Al Pacino", "country": "USA", "category": "Actor", "emoji": "🎭", "description": "Say hello to my little friend!"},
    {"name": "Robert De Niro", "country": "USA", "category": "Actor", "emoji": "😠", "description": "You talking to me?"},
    {"name": "Meryl Streep", "country": "USA", "category": "Actress", "emoji": "🏆", "description": "Greatest actress"},
    {"name": "Cate Blanchett", "country": "Australia", "category": "Actress", "emoji": "👑", "description": "Award-winning actress"},
    {"name": "Daniel Day-Lewis", "country": "UK", "category": "Actor", "emoji": "🎩", "description": "Method acting king"},
    {"name": "Anthony Hopkins", "country": "Wales", "category": "Actor", "emoji": "🧠", "description": "Hannibal Lecter"},
    {"name": "Samuel L. Jackson", "country": "USA", "category": "Actor", "emoji": "👨", "description": "Pulp Fiction star"},
    {"name": "Denzel Washington", "country": "USA", "category": "Actor", "emoji": "⭐", "description": "Award-winning actor"},
    {"name": "Tom Hanks", "country": "USA", "category": "Actor", "emoji": "🏃", "description": "Beloved actor"},
    {"name": "Julia Roberts", "country": "USA", "category": "Actress", "emoji": "😁", "description": "Pretty woman"},
    {"name": "Nicole Kidman", "country": "Australia", "category": "Actress", "emoji": "👠", "description": "Australian actress"},
    {"name": "George Clooney", "country": "USA", "category": "Actor", "emoji": "☕", "description": "Hollywood star"},
    {"name": "Matt Damon", "country": "USA", "category": "Actor", "emoji": "🚀", "description": "Bourne Identity star"},
    {"name": "Ben Affleck", "country": "USA", "category": "Actor", "emoji": "🦇", "description": "Batman actor"},
    {"name": "Jennifer Aniston", "country": "USA", "category": "Actress", "emoji": "☕", "description": "Friends star"},
    {"name": "David Schwimmer", "country": "USA", "category": "Actor", "emoji": "🦒", "description": "Ross from Friends"},
    {"name": "Courteney Cox", "country": "USA", "category": "Actress", "emoji": "👰", "description": "Monica from Friends"},
    {"name": "Lisa Kudrow", "country": "USA", "category": "Actress", "emoji": "🎵", "description": "Phoebe from Friends"},
    {"name": "Matthew Perry", "country": "USA", "category": "Actor", "emoji": "😏", "description": "Chandler from Friends"},
    {"name": "Matt LeBlanc", "country": "USA", "category": "Actor", "emoji": "🍕", "description": "Joey from Friends"},
    {"name": "Hugh Jackman", "country": "Australia", "category": "Actor", "emoji": "🦾", "description": "Wolverine actor"},
    {"name": "Ryan Reynolds", "country": "Canada", "category": "Actor", "emoji": "💀", "description": "Deadpool actor"},
    {"name": "Blake Lively", "country": "USA", "category": "Actress", "emoji": "👗", "description": "Gossip Girl star"},
    {"name": "Anne Hathaway", "country": "USA", "category": "Actress", "emoji": "👑", "description": "Princess Diaries star"},
    {"name": "Emma Stone", "country": "USA", "category": "Actress", "emoji": "🎭", "description": "La La Land star"},
    {"name": "Ryan Gosling", "country": "Canada", "category": "Actor", "emoji": "🚗", "description": "Drive star"},
    {"name": "Megan Fox", "country": "USA", "category": "Actress", "emoji": "🚗", "description": "Transformers star"},
    {"name": "Zac Efron", "country": "USA", "category": "Actor", "emoji": "🎶", "description": "High School Musical star"},
    {"name": "Mila Kunis", "country": "USA", "category": "Actress", "emoji": "👽", "description": "That 70s Show star"},
    {"name": "Ashton Kutcher", "country": "USA", "category": "Actor", "emoji": "🤵", "description": "Punk'd host"},
    {"name": "Channing Tatum", "country": "USA", "category": "Actor", "emoji": "💃", "description": "Magic Mike star"},
    {"name": "Sandra Bullock", "country": "USA", "category": "Actress", "emoji": "🚌", "description": "Speed star"},
    {"name": "Reese Witherspoon", "country": "USA", "category": "Actress", "emoji": "👑", "description": "Legally Blonde star"},
    {"name": "Vin Diesel", "country": "USA", "category": "Actor", "emoji": "🚗", "description": "Fast & Furious star"},
    {"name": "Paul Walker", "country": "USA", "category": "Actor", "emoji": "🚗", "description": "Fast & Furious star"},
    {"name": "Jason Statham", "country": "UK", "category": "Actor", "emoji": "🥊", "description": "Transporter star"},
    {"name": "Bruce Willis", "country": "USA", "category": "Actor", "emoji": "💥", "description": "Die Hard star"},
    {"name": "Arnold Schwarzenegger", "country": "Austria", "category": "Actor", "emoji": "💪", "description": "Terminator star"},
    {"name": "Sylvester Stallone", "country": "USA", "category": "Actor", "emoji": "🥊", "description": "Rocky star"},
    {"name": "Jackie Chan", "country": "Hong Kong", "category": "Actor", "emoji": "🥋", "description": "Martial arts legend"},
    {"name": "Jet Li", "country": "China", "category": "Actor", "emoji": "🥋", "description": "Martial arts star"},
    {"name": "Donnie Yen", "country": "China", "category": "Actor", "emoji": "🥋", "description": "Ip Man actor"},
    {"name": "Chuck Norris", "country": "USA", "category": "Actor", "emoji": "👊", "description": "Martial artist"},
    {"name": "Jean-Claude Van Damme", "country": "Belgium", "category": "Actor", "emoji": "🥋", "description": "Muscles from Brussels"},
    {"name": "Steven Seagal", "country": "USA", "category": "Actor", "emoji": "🥋", "description": "Action star"},
    {"name": "Dolph Lundgren", "country": "Sweden", "category": "Actor", "emoji": "🥊", "description": "Ivan Drago"},
    {"name": "Keira Knightley", "country": "UK", "category": "Actress", "emoji": "🏴‍☠️", "description": "Pirates of Caribbean star"},
    {"name": "Orlando Bloom", "country": "UK", "category": "Actor", "emoji": "🏹", "description": "Legolas actor"},
    {"name": "Viggo Mortensen", "country": "USA", "category": "Actor", "emoji": "👑", "description": "Aragorn actor"},
    {"name": "Ian McKellen", "country": "UK", "category": "Actor", "emoji": "🧙", "description": "Gandalf actor"},
    {"name": "Patrick Stewart", "country": "UK", "category": "Actor", "emoji": "🚀", "description": "Captain Picard"},
    {"name": "William Shatner", "country": "Canada", "category": "Actor", "emoji": "🚀", "description": "Captain Kirk"},
    {"name": "Chris Pine", "country": "USA", "category": "Actor", "emoji": "🚀", "description": "New Captain Kirk"},
    {"name": "Zoe Saldana", "country": "USA", "category": "Actress", "emoji": "🟢", "description": "Avatar and Guardians star"},
    {"name": "Josh Brolin", "country": "USA", "category": "Actor", "emoji": "🟣", "description": "Thanos actor"},
    {"name": "Tom Holland", "country": "UK", "category": "Actor", "emoji": "🕷️", "description": "Spider-Man actor"},
    {"name": "Tobey Maguire", "country": "USA", "category": "Actor", "emoji": "🕷️", "description": "Original Spider-Man"},
    {"name": "Andrew Garfield", "country": "USA", "category": "Actor", "emoji": "🕷️", "description": "Amazing Spider-Man"},
    {"name": "Willem Dafoe", "country": "USA", "category": "Actor", "emoji": "🟢", "description": "Green Goblin actor"},
    {"name": "Joaquin Phoenix", "country": "USA", "category": "Actor", "emoji": "🃏", "description": "Joker actor"},
    {"name": "Heath Ledger", "country": "Australia", "category": "Actor", "emoji": "🃏", "description": "Joker actor"},
    {"name": "Margot Robbie", "country": "Australia", "category": "Actress", "emoji": "🃏", "description": "Harley Quinn actress"},
    {"name": "Jared Leto", "country": "USA", "category": "Actor", "emoji": "🃏", "description": "Joker actor"},
    {"name": "Gal Gadot", "country": "Israel", "category": "Actress", "emoji": "🦸‍♀️", "description": "Wonder Woman actress"},
    {"name": "Henry Cavill", "country": "UK", "category": "Actor", "emoji": "🦸", "description": "Superman actor"},
    {"name": "Ben Stiller", "country": "USA", "category": "Actor", "emoji": "🎬", "description": "Comedy actor"},
    {"name": "Owen Wilson", "country": "USA", "category": "Actor", "emoji": "😯", "description": "Wow!"},
    {"name": "Vince Vaughn", "country": "USA", "category": "Actor", "emoji": "💬", "description": "Fast talker"},
    {"name": "Luke Wilson", "country": "USA", "category": "Actor", "emoji": "🤠", "description": "Actor"},
    {"name": "Adam Sandler", "country": "USA", "category": "Actor", "emoji": "😂", "description": "Comedy actor"},
    {"name": "Rob Schneider", "country": "USA", "category": "Actor", "emoji": "🤏", "description": "Comedy actor"},
    {"name": "David Spade", "country": "USA", "category": "Actor", "emoji": "😏", "description": "Comedy actor"},
    {"name": "Chris Rock", "country": "USA", "category": "Comedian", "emoji": "🎤", "description": "Comedian"},
    {"name": "Kevin Hart", "country": "USA", "category": "Comedian", "emoji": "😂", "description": "Comedian"},
    {"name": "Dave Chappelle", "country": "USA", "category": "Comedian", "emoji": "🎤", "description": "Comedian"},
    {"name": "Jerry Seinfeld", "country": "USA", "category": "Comedian", "emoji": "☕", "description": "Comedian"},
    {"name": "Larry David", "country": "USA", "category": "Comedian", "emoji": "😠", "description": "Comedian"},
    {"name": "Ricky Gervais", "country": "UK", "category": "Comedian", "emoji": "😏", "description": "Comedian"},
    {"name": "James Corden", "country": "UK", "category": "TV", "emoji": "🚗", "description": "TV host"},
    {"name": "Jimmy Fallon", "country": "USA", "category": "TV", "emoji": "😂", "description": "TV host"},
    {"name": "Jimmy Kimmel", "country": "USA", "category": "TV", "emoji": "😴", "description": "TV host"},
    {"name": "Stephen Colbert", "country": "USA", "category": "TV", "emoji": "🎭", "description": "TV host"},
    {"name": "Conan O'Brien", "country": "USA", "category": "TV", "emoji": "🦸‍♂️", "description": "TV host"},
    {"name": "Trevor Noah", "country": "South Africa", "category": "TV", "emoji": "🌍", "description": "TV host"},
    {"name": "John Oliver", "country": "UK", "category": "TV", "emoji": "🇬🇧", "description": "TV host"},
    {"name": "Seth Meyers", "country": "USA", "category": "TV", "emoji": "📰", "description": "TV host"}
]

# Create data directory if not exists
if not os.path.exists('data'):
    os.makedirs('data')

# Load user data
USER_DATA_FILE = 'data/users.json'
def load_user_data():
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_data = load_user_data()
    user_id = str(user.id)
    
    # Initialize user if not exists
    if user_id not in user_data:
        user_data[user_id] = {
            "name": user.first_name,
            "username": user.username,
            "join_date": datetime.now().isoformat(),
            "results": [],
            "total_points": 0,
            "total_matches": 0,
            "best_match": 0
        }
        save_user_data(user_data)
    
    # Generate website link with user ID
    website_link = f"https://ahmed-fawzy11.github.io/facematch-pro/?tgid={user_id}"
    
    await update.message.reply_text(
        f"🎭 **Welcome {user.first_name} to FaceMatch Pro!**\n\n"
        f"📸 *Discover which celebrity you look like!*\n\n"
        f"✨ **100% FREE Features:**\n"
        f"• Unlimited face matching\n"
        f"• 200+ celebrities database\n"
        f"• Personality analysis\n"
        f"• Save your results\n"
        f"• Share with friends\n\n"
        f"🚀 **Get Started:**\n"
        f"1. Visit our website:\n{website_link}\n"
        f"2. Allow camera access\n"
        f"3. Take a photo\n"
        f"4. Get your match!\n\n"
        f"🎯 **Bot Commands:**\n"
        f"/start - Welcome message\n"
        f"/try - Quick test (no camera)\n"
        f"/myresults - View your matches\n"
        f"/stats - Your statistics\n"
        f"/leaderboard - Top users\n"
        f"/help - Show all commands\n\n"
        f"📱 *Website works on all devices!*",
        parse_mode='Markdown'
    )

async def try_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /try command (quick test without camera)"""
    user = update.effective_user
    user_id = str(user.id)
    user_data = load_user_data()
    
    # Get random celebrity
    celeb = random.choice(CELEBRITIES)
    percent = random.randint(70, 98)
    traits = ["Natural leader", "Creative", "Charismatic", "Friendly", "Wise", "Ambitious"]
    
    # Save result
    if user_id in user_data:
        result = {
            "celebrity": celeb["name"],
            "match": percent,
            "date": datetime.now().isoformat(),
            "method": "bot_try"
        }
        user_data[user_id]["results"].append(result)
        user_data[user_id]["total_matches"] += 1
        user_data[user_id]["total_points"] += 10
        
        if percent > user_data[user_id]["best_match"]:
            user_data[user_id]["best_match"] = percent
            
        save_user_data(user_data)
    
    await update.message.reply_text(
        f"🎉 **QUICK MATCH RESULT!**\n\n"
        f"{celeb['emoji']} **You look like: {celeb['name']}**\n"
        f"📍 Country: {celeb['country']}\n"
        f"📌 Category: {celeb['category']}\n\n"
        f"📊 **Match Score: {percent}%**\n"
        f"🎭 *{celeb['description']}*\n"
        f"✨ *Personality: {random.choice(traits)}*\n\n"
        f"💡 *For better accuracy with camera:*\n"
        f"Visit our website!\n\n"
        f"🔁 /try - Try again\n"
        f"📋 /myresults - View all matches\n"
        f"📤 Share with friends!",
        parse_mode='Markdown'
    )

async def myresults(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myresults command"""
    user = update.effective_user
    user_id = str(user.id)
    user_data = load_user_data()
    
    if user_id not in user_data or len(user_data[user_id]["results"]) == 0:
        await update.message.reply_text(
            "📭 *You have no saved results yet!*\n\n"
            "Visit our website to get your first match:\n"
            f"https://ahmed-fawzy11.github.io/facematch-pro/?tgid={user_id}\n\n"
            "Or use /try for a quick test!",
            parse_mode='Markdown'
        )
        return
    
    results = user_data[user_id]["results"]
    
    # Sort by date (newest first)
    results.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    # Show last 5 results
    message = f"📋 **{user.first_name}'s Recent Matches:**\n\n"
    
    for i, result in enumerate(results[:5], 1):
        date_str = datetime.fromisoformat(result["date"]).strftime("%Y-%m-%d %H:%M")
        method = "🌐 Website" if result.get("method") == "website" else "🤖 Bot"
        
        message += f"{i}. **{result['celebrity']}** - {result['match']}%\n"
        message += f"   📅 {date_str} | {method}\n\n"
    
    message += f"📊 **Total Matches:** {len(results)}\n"
    message += f"⭐ **Best Match:** {user_data[user_id]['best_match']}%\n"
    message += f"🏆 **Total Points:** {user_data[user_id]['total_points']}\n\n"
    message += f"🔗 **Website:** https://ahmed-fawzy11.github.io/facematch-pro/?tgid={user_id}"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    user = update.effective_user
    user_id = str(user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        stats_data = {
            "total_matches": 0,
            "best_match": 0,
            "total_points": 0,
            "join_date": "Today"
        }
    else:
        join_date = datetime.fromisoformat(user_data[user_id]["join_date"])
        days_active = (datetime.now() - join_date).days + 1
        
        stats_data = {
            "total_matches": user_data[user_id]["total_matches"],
            "best_match": user_data[user_id]["best_match"],
            "total_points": user_data[user_id]["total_points"],
            "days_active": days_active
        }
    
    # Get most common celebrity
    if user_id in user_data and user_data[user_id]["results"]:
        celebrities = [r["celebrity"] for r in user_data[user_id]["results"]]
        from collections import Counter
        common = Counter(celebrities).most_common(1)
        top_celeb = common[0][0] if common else "None"
    else:
        top_celeb = "None"
    
    await update.message.reply_text(
        f"📊 **{user.first_name}'s Statistics:**\n\n"
        f"🎯 Total Matches: {stats_data['total_matches']}\n"
        f"👑 Best Match: {stats_data['best_match']}%\n"
        f"⭐ Most Common: {top_celeb}\n"
        f"🏆 Total Points: {stats_data['total_points']}\n"
        f"📅 Days Active: {stats_data.get('days_active', 1)}\n\n"
        f"🌐 **Website Activity:**\n"
        f"For detailed results with photos,\n"
        f"visit our website:\n"
        f"https://ahmed-fawzy11.github.io/facematch-pro/?tgid={user_id}\n\n"
        f"📋 /myresults - View all matches\n"
        f"🏆 /leaderboard - See top users",
        parse_mode='Markdown'
    )

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /leaderboard command"""
    user_data = load_user_data()
    
    if not user_data:
        await update.message.reply_text(
            "🏆 *Leaderboard is empty!*\n\n"
            "Be the first to get a match!",
            parse_mode='Markdown'
        )
        return
    
    # Create leaderboard based on points
    leaderboard_data = []
    for user_id, data in user_data.items():
        leaderboard_data.append({
            "name": data.get("name", "Unknown"),
            "points": data.get("total_points", 0),
            "matches": data.get("total_matches", 0),
            "best_match": data.get("best_match", 0)
        })
    
    # Sort by points
    leaderboard_data.sort(key=lambda x: x["points"], reverse=True)
    
    message = "🏆 **FaceMatch Pro Leaderboard**\n\n"
    
    medals = ["🥇", "🥈", "🥉", "4.", "5.", "6.", "7.", "8.", "9.", "10."]
    
    for i, user in enumerate(leaderboard_data[:10]):
        if i < 3:
            rank = medals[i]
        else:
            rank = medals[i]
        
        message += f"{rank} **{user['name']}**\n"
        message += f"   Points: {user['points']} | Matches: {user['matches']} | Best: {user['best_match']}%\n\n"
    
    message += f"👤 **Total Users:** {len(user_data)}\n"
    message += "📊 Updated: " + datetime.now().strftime("%Y-%m-%d %H:%M")
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "🆘 **Available Commands:**\n\n"
        "/start - Welcome message & website link\n"
        "/try - Quick test (no camera needed)\n"
        "/myresults - View your saved matches\n"
        "/stats - Your statistics\n"
        "/leaderboard - Top users leaderboard\n"
        "/help - Show this message\n\n"
        "🌐 **Website Features:**\n"
        "• Camera face matching\n"
        "• Photo filters\n"
        "• Personality analysis\n"
        "• Save results with photos\n"
        "• User profiles\n\n"
        "🚀 **Get Started:**\n"
        "Use /start to get your personal website link!",
        parse_mode='Markdown'
    )

async def handle_website_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle results sent from website"""
    # This would be called via webhook
    # For now, just log it
    logger.info("Website result received")

def main():
    """Start the bot"""
    # PUT YOUR TOKEN HERE
    TOKEN = "8343772483:AAElQuvcUwMROBW3PKbX1B4V0Sq2wHQgZsw"
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("try", try_cmd))
    app.add_handler(CommandHandler("myresults", myresults))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("help", help_cmd))
    
    # Start bot
    print("🤖 FaceMatch Pro Bot is running...")
    print("📡 Waiting for messages...")
    print("💾 User data storage: data/users.json")
    print("🌐 Website: https://ahmed-fawzy11.github.io/facematch-pro/")
    logger.info("Bot started successfully")
    
    # Run bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
