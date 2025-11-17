import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const CSCourseRecommenderApp());
}

class CSCourseRecommenderApp extends StatelessWidget {
  const CSCourseRecommenderApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CS Course Recommender',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      themeMode: ThemeMode.system,
      home: const HomeScreen(),
    );
  }
}