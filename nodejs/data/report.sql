/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50617
Source Host           : localhost:3306
Source Database       : crawl

Target Server Type    : MYSQL
Target Server Version : 50617
File Encoding         : 65001

Date: 2017-10-24 16:13:33
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `crawl_jin10_cftc_c_report`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_cftc_c_report`;
CREATE TABLE `crawl_jin10_cftc_c_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `long_positions` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '多头仓位',
  `short_position` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '空头仓位',
  `cat_name` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '种类',
  `time` date NOT NULL,
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='美国商品期货交易委员会CFTC商品类非商业持仓报告';

-- ----------------------------
-- Records of crawl_jin10_cftc_c_report
-- ----------------------------

-- ----------------------------
-- Table structure for `crawl_jin10_cftc_merchant_currency`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_cftc_merchant_currency`;
CREATE TABLE `crawl_jin10_cftc_merchant_currency` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `long_positions` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '多头仓位',
  `short_position` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '空头仓位',
  `cat_name` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '种类',
  `time` date NOT NULL,
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='美国商品期货交易委员会CFTC外汇类商业持仓报告';

-- ----------------------------
-- Records of crawl_jin10_cftc_merchant_currency
-- ----------------------------

-- ----------------------------
-- Table structure for `crawl_jin10_cftc_merchant_goods`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_cftc_merchant_goods`;
CREATE TABLE `crawl_jin10_cftc_merchant_goods` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `long_positions` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '多头仓位',
  `short_position` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '空头仓位',
  `cat_name` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '种类',
  `time` date NOT NULL,
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='美国商品期货交易委员会CFTC商品类商业持仓报告';

-- ----------------------------
-- Records of crawl_jin10_cftc_merchant_goods
-- ----------------------------

-- ----------------------------
-- Table structure for `crawl_jin10_cftc_nc_report`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_cftc_nc_report`;
CREATE TABLE `crawl_jin10_cftc_nc_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `long_positions` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '多头仓位',
  `short_position` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '空头仓位',
  `cat_name` varchar(32) COLLATE utf8_unicode_ci NOT NULL COMMENT '种类',
  `time` date NOT NULL,
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='美国商品期货交易委员会CFTC外汇类非商业持仓报告';

-- ----------------------------
-- Records of crawl_jin10_cftc_nc_report
-- ----------------------------

-- ----------------------------
-- Table structure for `crawl_jin10_cme_energy_report`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_cme_energy_report`;
CREATE TABLE `crawl_jin10_cme_energy_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat_name` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '商品',
  `type_name` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '类型',
  `time` date NOT NULL,
  `transaction_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '电子交易合约',
  `inside_closing_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '场内成交合约',
  `outside_closing_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '场外成交合约',
  `volume` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '成交量',
  `open_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '未平仓合约',
  `position_change` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '持仓变化',
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='芝加哥商业交易所（CME）能源类商品成交量报告';

-- ----------------------------
-- Records of crawl_jin10_cme_energy_report
-- ----------------------------

-- ----------------------------
-- Table structure for `crawl_jin10_cme_fx_report`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_cme_fx_report`;
CREATE TABLE `crawl_jin10_cme_fx_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat_name` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '商品',
  `type_name` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '类型',
  `time` date NOT NULL,
  `transaction_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '电子交易合约',
  `inside_closing_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '场内成交合约',
  `outside_closing_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '场外成交合约',
  `volume` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '成交量',
  `open_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '未平仓合约',
  `position_change` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='芝加哥商业交易所（CME）外汇类商品成交量报告';

-- ----------------------------
-- Records of crawl_jin10_cme_fx_report
-- ----------------------------

-- ----------------------------
-- Table structure for `crawl_jin10_cme_report`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_cme_report`;
CREATE TABLE `crawl_jin10_cme_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat_name` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '商品',
  `type_name` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '类型',
  `time` date NOT NULL,
  `transaction_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '电子交易合约',
  `inside_closing_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '场内成交合约',
  `outside_closing_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '场外成交合约',
  `volume` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '成交量',
  `open_contract` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '未平仓合约',
  `position_change` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='芝加哥商业交易所（CME）金属类商品成交量报告';

-- ----------------------------
-- Records of crawl_jin10_cme_report
-- ----------------------------

-- ----------------------------
-- Table structure for `crawl_jin10_etf`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_etf`;
CREATE TABLE `crawl_jin10_etf` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat_name` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `time` date NOT NULL,
  `total_inventory` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '总库存',
  `increase` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '增持减持',
  `total_value` varchar(32) COLLATE utf8_unicode_ci NOT NULL COMMENT '总价值',
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='全球最大白银ETF--iShares Silver Trust持仓报告';

-- ----------------------------
-- Records of crawl_jin10_etf
-- ----------------------------

-- ----------------------------
-- Table structure for `crawl_jin10_lme_report`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_lme_report`;
CREATE TABLE `crawl_jin10_lme_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cat_name` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
  `stock` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '库存',
  `registered_warehouse_receipt` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '注册仓单',
  `canceled_warehouse_receipt` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '注销仓单',
  `time` date NOT NULL,
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='伦敦金属交易所（LME）库存报告';

-- ----------------------------
-- Records of crawl_jin10_lme_report
-- ----------------------------

-- ----------------------------
-- Table structure for `crawl_jin10_lme_traders_report`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_lme_traders_report`;
CREATE TABLE `crawl_jin10_lme_traders_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `long_positions` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '多头仓位',
  `short_position` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '空头仓位',
  `cat_name` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '种类',
  `time` date NOT NULL,
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='伦敦金属交易所（LME）持仓报告';

-- ----------------------------
-- Records of crawl_jin10_lme_traders_report
-- ----------------------------

-- ----------------------------
-- Table structure for `crawl_jin10_nonfarm_payrolls`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_nonfarm_payrolls`;
CREATE TABLE `crawl_jin10_nonfarm_payrolls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` date NOT NULL,
  `cat_name` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `former_value` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '前值',
  `pub_value` varchar(16) COLLATE utf8_unicode_ci NOT NULL COMMENT '今值',
  `expected_value` varchar(16) COLLATE utf8_unicode_ci NOT NULL,
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='美国非农就业人数报告';

-- ----------------------------
-- Records of crawl_jin10_nonfarm_payrolls
-- ----------------------------

-- ----------------------------
-- Table structure for `crawl_jin10_ssi_trends`
-- ----------------------------
DROP TABLE IF EXISTS `crawl_jin10_ssi_trends`;
CREATE TABLE `crawl_jin10_ssi_trends` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `platform` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `type` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  `long_position` decimal(4,2) NOT NULL,
  `time` datetime NOT NULL,
  `updated_time` datetime NOT NULL,
  `created_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_time` (`time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='投机情绪报告';

-- ----------------------------
-- Records of crawl_jin10_ssi_trends
-- ----------------------------
