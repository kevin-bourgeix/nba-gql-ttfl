from nba_api.stats.static import teams as nba_teams
from nba_api.stats.endpoints import teamplayerdashboard
from ariadne import gql, QueryType, make_executable_schema, ObjectType
from ariadne.asgi import GraphQL

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


@query.field("team")
def resolve_team(*_, abrv: str):
    return nba_teams.find_team_by_abbreviation(abrv)


@query.field("teams")
def resolve_teams(*_):
    teams = nba_teams.get_teams()
    return teams


team_resolver = ObjectType("Team")


@team_resolver.field("players")
def resolve_players(team, *_):
    endpoint = teamplayerdashboard.TeamPlayerDashboard(
        team_id=team['id']
    )

    players = endpoint.get_data_frames()[1][["PLAYER_ID", "PLAYER_NAME", "GP"]].to_dict('records')
    
    return list(map(lambda x: {
        "id": x["PLAYER_ID"],
        "name": x["PLAYER_NAME"],
        "gp": x["GP"]
    }, players))


schema = make_executable_schema(type_defs, query, team_resolver)

app = GraphQL(schema, debug=True)
