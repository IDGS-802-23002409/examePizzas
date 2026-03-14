-- Respaldo de la base de datos: pizzas
-- Fecha: 2026-03-13 19:16:54.652055

CREATE DATABASE IF NOT EXISTS `pizzas` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `pizzas`;

SET FOREIGN_KEY_CHECKS = 0;

-- Tabla: clientes
DROP TABLE IF EXISTS `clientes`;
CREATE TABLE `clientes` (
  `id_cliente` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `clientes` (`id_cliente`, `nombre`, `direccion`, `telefono`) VALUES ('1', 'Mario Juarez', '5 de mayo', '477-787-23');

-- Tabla: detalle_pedido
DROP TABLE IF EXISTS `detalle_pedido`;
CREATE TABLE `detalle_pedido` (
  `id_detalle` int(11) NOT NULL AUTO_INCREMENT,
  `id_pedido` int(11) NOT NULL,
  `id_pizza` int(11) NOT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `id_pedido` (`id_pedido`),
  KEY `id_pizza` (`id_pizza`),
  CONSTRAINT `1` FOREIGN KEY (`id_pedido`) REFERENCES `pedidos` (`id_pedido`),
  CONSTRAINT `2` FOREIGN KEY (`id_pizza`) REFERENCES `pizzas` (`id_pizza`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `detalle_pedido` (`id_detalle`, `id_pedido`, `id_pizza`, `cantidad`, `subtotal`) VALUES ('1', '1', '2', '2', '180.00');

-- Tabla: pedidos
DROP TABLE IF EXISTS `pedidos`;
CREATE TABLE `pedidos` (
  `id_pedido` int(11) NOT NULL AUTO_INCREMENT,
  `id_cliente` int(11) NOT NULL,
  `fecha` date DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_pedido`),
  KEY `id_cliente` (`id_cliente`),
  CONSTRAINT `1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `pedidos` (`id_pedido`, `id_cliente`, `fecha`, `total`) VALUES ('1', '1', '2026-03-13', '180.00');

-- Tabla: pizzas
DROP TABLE IF EXISTS `pizzas`;
CREATE TABLE `pizzas` (
  `id_pizza` int(11) NOT NULL AUTO_INCREMENT,
  `tamano` varchar(20) DEFAULT NULL,
  `ingredientes` varchar(200) DEFAULT NULL,
  `precio` decimal(8,2) DEFAULT NULL,
  PRIMARY KEY (`id_pizza`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `pizzas` (`id_pizza`, `tamano`, `ingredientes`, `precio`) VALUES ('1', 'Chica', '', '40.00');
INSERT INTO `pizzas` (`id_pizza`, `tamano`, `ingredientes`, `precio`) VALUES ('2', 'Mediana', '', '80.00');
INSERT INTO `pizzas` (`id_pizza`, `tamano`, `ingredientes`, `precio`) VALUES ('3', 'Grande', '', '120.00');

SET FOREIGN_KEY_CHECKS = 1;
