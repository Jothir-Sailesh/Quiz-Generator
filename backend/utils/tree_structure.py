"""
Tree Structure Implementation - Hierarchical Question Organization
Organizes questions in a tree structure: Subject → Topic → Difficulty → Questions
"""

from typing import Dict, List, Optional, Any
from collections import defaultdict
from backend.models.question import QuestionResponse, DifficultyLevel

class QuestionNode:
    """Individual node in the question tree structure"""
    
    def __init__(self, value: Any, node_type: str):
        self.value = value
        self.node_type = node_type  # 'subject', 'topic', 'difficulty', 'question'
        self.children: Dict[str, 'QuestionNode'] = {}
        self.questions: List[QuestionResponse] = []
        self.metadata = {
            'count': 0,
            'difficulty_distribution': defaultdict(int),
            'success_rate': 0.0
        }
    
    def add_child(self, key: str, child: 'QuestionNode'):
        """Add a child node to the current node"""
        self.children[key] = child
        self.metadata['count'] += 1
    
    def get_child(self, key: str) -> Optional['QuestionNode']:
        """Get a child node by key"""
        return self.children.get(key)
    
    def get_all_questions(self) -> List[QuestionResponse]:
        """Recursively get all questions from this node and its children"""
        all_questions = self.questions.copy()
        
        for child in self.children.values():
            all_questions.extend(child.get_all_questions())
        
        return all_questions

class QuestionTree:
    """
    Tree data structure for hierarchical question organization
    Structure: Root → Subject → Topic → Difficulty → Questions
    """
    
    def __init__(self):
        self.root = QuestionNode("root", "root")
        self.total_questions = 0
        
    def add_question(self, question: QuestionResponse):
        """
        Add a question to the tree structure
        Automatically creates intermediate nodes if they don't exist
        """
        # Navigate/create subject node
        subject_node = self.root.get_child(question.subject)
        if not subject_node:
            subject_node = QuestionNode(question.subject, "subject")
            self.root.add_child(question.subject, subject_node)
        
        # Navigate/create topic node
        topic_node = subject_node.get_child(question.topic)
        if not topic_node:
            topic_node = QuestionNode(question.topic, "topic")
            subject_node.add_child(question.topic, topic_node)
        
        # Navigate/create difficulty node
        difficulty_key = question.difficulty.value
        difficulty_node = topic_node.get_child(difficulty_key)
        if not difficulty_node:
            difficulty_node = QuestionNode(question.difficulty, "difficulty")
            topic_node.add_child(difficulty_key, difficulty_node)
        
        # Add question to the difficulty node
        difficulty_node.questions.append(question)
        
        # Update metadata
        self._update_metadata(question)
        self.total_questions += 1
    
    def get_questions_by_criteria(self, 
                                 subject: Optional[str] = None,
                                 topic: Optional[str] = None, 
                                 difficulty: Optional[DifficultyLevel] = None,
                                 limit: Optional[int] = None) -> List[QuestionResponse]:
        """
        Retrieve questions based on hierarchical criteria
        Supports flexible filtering at different tree levels
        """
        questions = []
        
        # Start from root or specific subject
        if subject:
            subject_node = self.root.get_child(subject)
            if not subject_node:
                return questions
            search_nodes = [subject_node]
        else:
            search_nodes = list(self.root.children.values())
        
        # Filter by topic if specified
        if topic:
            filtered_nodes = []
            for node in search_nodes:
                topic_node = node.get_child(topic)
                if topic_node:
                    filtered_nodes.append(topic_node)
            search_nodes = filtered_nodes
        
        # Filter by difficulty if specified
        if difficulty:
            filtered_nodes = []
            for node in search_nodes:
                if node.node_type == "topic":
                    difficulty_node = node.get_child(difficulty.value)
                    if difficulty_node:
                        filtered_nodes.append(difficulty_node)
                elif node.node_type == "subject":
                    # Search all topics in the subject
                    for topic_node in node.children.values():
                        difficulty_node = topic_node.get_child(difficulty.value)
                        if difficulty_node:
                            filtered_nodes.append(difficulty_node)
            search_nodes = filtered_nodes
        
        # Collect questions from filtered nodes
        for node in search_nodes:
            questions.extend(node.get_all_questions())
        
        # Apply limit if specified
        if limit and len(questions) > limit:
            questions = questions[:limit]
        
        return questions
    
    def get_tree_structure(self) -> Dict[str, Any]:
        """
        Get a dictionary representation of the tree structure
        Useful for frontend navigation and analytics
        """
        def build_structure(node: QuestionNode) -> Dict[str, Any]:
            structure = {
                'type': node.node_type,
                'value': node.value,
                'question_count': len(node.questions),
                'total_count': node.metadata['count'],
                'children': {}
            }
            
            for key, child in node.children.items():
                structure['children'][key] = build_structure(child)
            
            return structure
        
        return build_structure(self.root)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the question tree"""
        stats = {
            'total_questions': self.total_questions,
            'subjects': len(self.root.children),
            'subjects_detail': {}
        }
        
        for subject_key, subject_node in self.root.children.items():
            subject_stats = {
                'topics': len(subject_node.children),
                'total_questions': len(subject_node.get_all_questions()),
                'difficulty_distribution': defaultdict(int),
                'topics_detail': {}
            }
            
            for topic_key, topic_node in subject_node.children.items():
                topic_questions = topic_node.get_all_questions()
                topic_stats['topics_detail'][topic_key] = {
                    'question_count': len(topic_questions),
                    'difficulties': list(topic_node.children.keys())
                }
                
                # Count difficulty distribution
                for question in topic_questions:
                    subject_stats['difficulty_distribution'][question.difficulty.value] += 1
            
            stats['subjects_detail'][subject_key] = subject_stats
        
        return stats
    
    def _update_metadata(self, question: QuestionResponse):
        """Update tree metadata when a question is added"""
        # This method can be expanded to maintain various statistics
        # like success rates, difficulty distributions, etc.
        pass
    
    def remove_question(self, question_id: str) -> bool:
        """Remove a question from the tree by ID"""
        def search_and_remove(node: QuestionNode) -> bool:
            # Check questions in current node
            for i, question in enumerate(node.questions):
                if str(question.id) == question_id:
                    node.questions.pop(i)
                    self.total_questions -= 1
                    return True
            
            # Search in children
            for child in node.children.values():
                if search_and_remove(child):
                    return True
            
            return False
        
        return search_and_remove(self.root)