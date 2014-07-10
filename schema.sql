-- MySQL dump 10.13  Distrib 5.6.19, for osx10.7 (x86_64)
--
-- Host: localhost    Database: listener
-- ------------------------------------------------------
-- Server version	5.6.19

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `block`
--

DROP TABLE IF EXISTS `block`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `block` (
  `block_hash` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `block_height` int(11) DEFAULT NULL,
  `is_orphaned` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`block_hash`),
  KEY `ix_block_block_hash` (`block_hash`),
  KEY `ix_block_block_height` (`block_height`),
  KEY `ix_block_is_orphaned` (`is_orphaned`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `node`
--

DROP TABLE IF EXISTS `node`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `node` (
  `ip_address` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `timestamp` bigint(20) NOT NULL,
  `port` int(11) NOT NULL,
  `city` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `start_height` bigint(20) DEFAULT NULL,
  `country` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `hostname` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `time_zone` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `version` int(11) DEFAULT NULL,
  `user_agent` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `org` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `asn` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `address` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`ip_address`),
  KEY `ix_node_asn` (`asn`),
  KEY `ix_node_city` (`city`),
  KEY `ix_node_country` (`country`),
  KEY `ix_node_hostname` (`hostname`),
  KEY `ix_node_latitude` (`latitude`),
  KEY `ix_node_longitude` (`longitude`),
  KEY `ix_node_org` (`org`),
  KEY `ix_node_start_height` (`start_height`),
  KEY `ix_node_time_zone` (`time_zone`),
  KEY `ix_node_timestamp` (`timestamp`),
  KEY `ix_node_user_agent` (`user_agent`),
  KEY `ix_node_version` (`version`),
  KEY `ix_node_ip_address` (`ip_address`),
  KEY `ix_node_address` (`address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `node_activity`
--

DROP TABLE IF EXISTS `node_activity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `node_activity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `address` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_node_activity_created_at` (`created_at`),
  KEY `ix_node_activity_status` (`status`),
  KEY `ix_node_activity_address` (`address`),
  KEY `ix_node_activity_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=237 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `schema_migrations`
--

DROP TABLE IF EXISTS `schema_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `schema_migrations` (
  `version` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  UNIQUE KEY `unique_schema_migrations` (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transaction`
--

DROP TABLE IF EXISTS `transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transaction` (
  `txid` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `value` decimal(15,8) DEFAULT NULL,
  `block_height` int(11) DEFAULT NULL,
  `has_multisig` tinyint(1) DEFAULT NULL,
  `has_nulldata` tinyint(1) DEFAULT NULL,
  `has_pubkey` tinyint(1) DEFAULT NULL,
  `has_pubkeyhash` tinyint(1) DEFAULT NULL,
  `has_scripthash` tinyint(1) DEFAULT NULL,
  `block_hash` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`txid`),
  KEY `ix_transaction_created_at` (`created_at`),
  KEY `ix_transaction_value` (`value`),
  KEY `ix_transaction_block_height` (`block_height`),
  KEY `ix_transaction_has_multisig` (`has_multisig`),
  KEY `ix_transaction_has_nulldata` (`has_nulldata`),
  KEY `ix_transaction_has_pubkey` (`has_pubkey`),
  KEY `ix_transaction_has_pubkeyhash` (`has_pubkeyhash`),
  KEY `ix_transaction_has_scripthash` (`has_scripthash`),
  KEY `ix_transaction_block_hash` (`block_hash`),
  KEY `ix_transaction_txid` (`txid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transaction_address_info`
--

DROP TABLE IF EXISTS `transaction_address_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transaction_address_info` (
  `address` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `coinbase` int(11) DEFAULT NULL,
  `balance` decimal(15,8) DEFAULT NULL,
  `received_value` decimal(15,8) DEFAULT NULL,
  `spent_value` decimal(15,8) DEFAULT NULL,
  `vin_count` int(11) DEFAULT NULL,
  `vout_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`address`),
  KEY `ix_transaction_address_info_coinbase` (`coinbase`),
  KEY `ix_transaction_address_info_address` (`address`),
  KEY `ix_transaction_address_info_balance` (`balance`),
  KEY `ix_transaction_address_info_received_value` (`received_value`),
  KEY `ix_transaction_address_info_spent_value` (`spent_value`),
  KEY `ix_transaction_address_info_vin_count` (`vin_count`),
  KEY `ix_transaction_address_info_vout_count` (`vout_count`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transaction_address_info_update`
--

DROP TABLE IF EXISTS `transaction_address_info_update`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transaction_address_info_update` (
  `block_height` int(11) NOT NULL AUTO_INCREMENT,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`block_height`),
  KEY `ix_transaction_address_info_update_block_height` (`block_height`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transaction_info`
--

DROP TABLE IF EXISTS `transaction_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transaction_info` (
  `txid` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `relayed_from` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `json_string` text COLLATE utf8_unicode_ci,
  `received_at` datetime DEFAULT NULL,
  PRIMARY KEY (`txid`,`relayed_from`),
  KEY `ix_transaction_info_created_at` (`created_at`),
  KEY `ix_transaction_info_received_at` (`received_at`),
  KEY `ix_transaction_info_relayed_from` (`relayed_from`),
  KEY `ix_transaction_info_txid` (`txid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transaction_vin`
--

DROP TABLE IF EXISTS `transaction_vin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transaction_vin` (
  `txid` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `offset` int(11) NOT NULL,
  `output_txid` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `vout_offset` int(11) DEFAULT NULL,
  PRIMARY KEY (`txid`,`offset`),
  KEY `ix_transaction_input_output_txid_and_vout_index` (`output_txid`,`vout_offset`),
  KEY `ix_transaction_vin_offset` (`offset`),
  KEY `ix_transaction_vin_output_txid` (`output_txid`),
  KEY `ix_transaction_vin_txid` (`txid`),
  KEY `ix_transaction_vin_vout_offset` (`vout_offset`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transaction_vout`
--

DROP TABLE IF EXISTS `transaction_vout`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transaction_vout` (
  `txid` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `offset` int(11) NOT NULL,
  `address` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `block_hash` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `block_height` int(11) DEFAULT NULL,
  `value` decimal(15,8) DEFAULT NULL,
  `is_from_coinbase` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`txid`,`offset`),
  KEY `ix_transaction_vout_address` (`address`),
  KEY `ix_transaction_vout_block_hash` (`block_hash`),
  KEY `ix_transaction_vout_block_height` (`block_height`),
  KEY `ix_transaction_vout_is_from_coinbase` (`is_from_coinbase`),
  KEY `ix_transaction_vout_offset` (`offset`),
  KEY `ix_transaction_vout_txid` (`txid`),
  KEY `ix_transaction_vout_value` (`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-07-09 17:38:36
