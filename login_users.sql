-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 25, 2024 at 07:41 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `login_users`
--

-- --------------------------------------------------------

--
-- Table structure for table `attendance`
--

CREATE TABLE `attendance` (
  `Name` varchar(50) NOT NULL,
  `Status` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `attendance`
--

INSERT INTO `attendance` (`Name`, `Status`) VALUES
('Nobita', 'Present'),
('Doremon', 'Present'),
('Chota Bheem', 'Absent'),
('Chutki', 'Present'),
('Raju', 'Absent'),
('Jaggu', 'Present');

-- --------------------------------------------------------

--
-- Table structure for table `internal_1`
--

CREATE TABLE `internal_1` (
  `Name` varchar(30) NOT NULL,
  `Tamil` int(11) NOT NULL,
  `English` int(11) NOT NULL,
  `Maths` int(11) NOT NULL,
  `Science` int(11) NOT NULL,
  `Social` int(11) NOT NULL,
  `Total` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `internal_1`
--

INSERT INTO `internal_1` (`Name`, `Tamil`, `English`, `Maths`, `Science`, `Social`, `Total`) VALUES
('Nobita', 50, 60, 70, 65, 95, 340),
('Doremon', 100, 100, 100, 100, 100, 500),
('Chota Bheem', 50, 80, 80, 65, 95, 360),
('Chutki', 50, 60, 70, 65, 95, 340),
('Raju', 100, 50, 70, 55, 90, 365),
('Jaggu', 50, 70, 70, 65, 95, 350);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `Username` varchar(500) NOT NULL,
  `email` varchar(500) NOT NULL,
  `phone_number` bigint(200) NOT NULL,
  `password` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
