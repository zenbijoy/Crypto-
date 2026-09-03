package com.example.core.database

import android.content.Context
import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface CryptoScopeDao {
    @Query("SELECT * FROM watchlists")
    fun getAllWatchlists(): Flow<List<WatchlistEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertWatchlist(item: WatchlistEntity)

    @Delete
    suspend fun deleteWatchlist(item: WatchlistEntity)

    @Query("SELECT * FROM alert_rules")
    fun getAllAlerts(): Flow<List<AlertRuleEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAlert(alert: AlertRuleEntity)

    @Query("DELETE FROM alert_rules WHERE id = :alertId")
    suspend fun deleteAlertById(alertId: String)

    @Query("UPDATE alert_rules SET status = :status WHERE id = :alertId")
    suspend fun updateAlertStatus(alertId: String, status: String)

    @Query("SELECT * FROM paper_positions")
    fun getAllPaperPositions(): Flow<List<PaperPositionEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPaperPosition(position: PaperPositionEntity)

    @Query("DELETE FROM paper_positions WHERE id = :positionId")
    suspend fun deletePaperPosition(positionId: String)

    @Query("SELECT * FROM market_cache")
    fun getMarketCache(): Flow<List<MarketCacheEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun updateMarketCache(items: List<MarketCacheEntity>)
}

@Database(
    entities = [
        WatchlistEntity::class,
        AlertRuleEntity::class,
        PaperPositionEntity::class,
        MarketCacheEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class CryptoScopeDatabase : RoomDatabase() {
    abstract fun dao(): CryptoScopeDao

    companion object {
        @Volatile
        private var INSTANCE: CryptoScopeDatabase? = null

        fun getDatabase(context: Context): CryptoScopeDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    CryptoScopeDatabase::class.java,
                    "cryptoscope_db"
                ).fallbackToDestructiveMigration().build()
                INSTANCE = instance
                instance
            }
        }
    }
}
