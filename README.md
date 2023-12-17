# NBA Gql POC
A quick PoC of a Graphql app for computing stuff for a fantasy league

> [!NOTE]
> I am trash at using Python, don't take this code seriously

## Running
```shell
make run
```

## Exemple request
Get all players from the bucks
```gql
query {
    team(abrv: "MIL") {
        id
        full_name
        abbreviation
        players {
            id
            name
            gp
        }
    }
}
```