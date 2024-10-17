import os
from nba_api.stats.static import teams as nba_teams
from nba_api.stats.endpoints import teamplayerdashboard
from ariadne import gql, QueryType, make_executable_schema, ObjectType
from ariadne.asgi import GraphQL
from pymongo import MongoClient

type_defs = gql("""
    type Team {
        id: ID!
        full_name: String!
        abbreviation: String!
        players: [Player!]!
    }
    
    type Player {
        id: ID!
        name: String!
        gp: Int!
    }
    
    type Query {
        team(abrv: String!): Team!
        teams: [Team!]!
    }
""")

query = QueryType()

# MongoDB connection setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "nba_db")
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
players_collection = db["players"]
teams_collection = db["teams"]

@query.field("team")
def resolve_team(*_, abrv: str):
    return nba_teams.find_team_by_abbreviation(abrv)


@query.field("teams")
def resolve_teams(*_):
    teams = nba_teams.get_teams()
    
    # Upload team data to MongoDB
    for team in teams:
        teams_collection.update_one(
            {"id": team["id"]},
            {"$set": {
                "id": team["id"],
                "full_name": team["full_name"],
                "abbreviation": team["abbreviation"]
            }},
            upsert=True
        )
    
    return teams


team_resolver = ObjectType("Team")


@team_resolver.field("players")
def resolve_players(team, *_):
    endpoint = teamplayerdashboard.TeamPlayerDashboard(
        team_id=team['id']
    )

    players = endpoint.get_data_frames()[1][["PLAYER_ID", "PLAYER_NAME", "GP"]].to_dict('records')
    
    # Upload player data to MongoDB
    for player in players:
        players_collection.update_one(
            {"id": player["PLAYER_ID"]},
            {"$set": {
                "id": player["PLAYER_ID"],
                "name": player["PLAYER_NAME"],
                "gp": player["GP"]
            }},
            upsert=True
        )
    
    return list(map(lambda x: {
        "id": x["PLAYER_ID"],
        "name": x["PLAYER_NAME"],
        "gp": x["GP"]
    }, players))


schema = make_executable_schema(type_defs, query, team_resolver)

app = GraphQL(schema, debug=True)
