---
name: db-explore
description: MongoDB database exploration for understanding game data, debugging, and investigation. Auto-applies when discussing database structure or debugging data issues.
allowed-tools: Bash, Read
---

# DB Explore Skill

MongoDB exploration for OpenCivilizations game.

## Database Collections

| Collection | Purpose |
|------------|---------|
| users | Player accounts and authentication |
| bases | Player base layouts and buildings |
| clans | Alliance/clan data |
| battles | Battle replays and results |
| leaderboards | Rankings cache |

## MongoDB Shell Commands

### Connect
```bash
mongosh "mongodb://localhost:27017/dominations"
```

### List Collections
```javascript
db.getCollectionNames()
```

### Sample Documents
```javascript
// Get sample user
db.users.findOne()

// Get sample base with buildings
db.bases.findOne({}, { buildings: { $slice: 5 } })

// Get recent battles
db.battles.find().sort({ createdAt: -1 }).limit(5)
```

### Count Documents
```javascript
// Total users
db.users.countDocuments()

// Active players (last 7 days)
db.users.countDocuments({ lastLogin: { $gte: new Date(Date.now() - 7*24*60*60*1000) } })
```

### Find Documents
```javascript
// Find user by name
db.users.findOne({ username: "player1" })

// Find bases with specific building
db.bases.find({ "buildings.type": "townCenter" })

// Find clan members
db.clans.findOne({ name: "Warriors" }, { members: 1 })
```

### Aggregations
```javascript
// Count buildings by type across all bases
db.bases.aggregate([
  { $unwind: "$buildings" },
  { $group: { _id: "$buildings.type", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])

// Average resources per player
db.users.aggregate([
  { $group: {
    _id: null,
    avgGold: { $avg: "$resources.gold" },
    avgFood: { $avg: "$resources.food" }
  }}
])
```

## Common Queries

### Player Investigation
```javascript
// Get player with full base
db.users.aggregate([
  { $match: { username: "player1" } },
  { $lookup: {
    from: "bases",
    localField: "_id",
    foreignField: "userId",
    as: "base"
  }}
])
```

### Battle Analysis
```javascript
// Get battle with attacker and defender info
db.battles.aggregate([
  { $match: { _id: ObjectId("...") } },
  { $lookup: { from: "users", localField: "attackerId", foreignField: "_id", as: "attacker" } },
  { $lookup: { from: "users", localField: "defenderId", foreignField: "_id", as: "defender" } }
])
```

### Leaderboard
```javascript
// Top 10 by trophies
db.users.find({}, { username: 1, trophies: 1 })
  .sort({ trophies: -1 })
  .limit(10)
```

## Important Notes

- **Read-only** - Never modify production data
- **Use limits** - Large collections need `.limit()`
- **Index awareness** - Check indexes before heavy queries
- **Redis for sessions** - Active game state is in Redis, not MongoDB
