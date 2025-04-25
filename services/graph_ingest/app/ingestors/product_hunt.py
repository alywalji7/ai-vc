"""
Product Hunt Connector for Graph Ingest Service.

This module fetches product launch data from Product Hunt and creates
entities and relationships in the knowledge graph.
"""
import os
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import httpx

from ..db import engine, get_session
from ..models.product_hunt import ProductLaunchEvent, ProductLaunchRelationship
from ..models.company import Company

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
API_BASE_URL = "https://api.producthunt.com/v2/api/graphql"
DEFAULT_TOPIC_FILTERS = ["ARTIFICIAL_INTELLIGENCE", "PRODUCTIVITY", "DEVELOPER_TOOLS", "SaaS"]
DEFAULT_DAYS_LOOKBACK = 30


class ProductHuntConnector:
    """
    Connector for fetching product launch data from Product Hunt.
    """
    
    def __init__(self):
        """
        Initialize the Product Hunt connector.
        
        Requires PRODUCT_HUNT_API_KEY environment variable to be set.
        """
        self.api_key = os.environ.get("PRODUCT_HUNT_API_KEY")
        if not self.api_key:
            logger.warning("PRODUCT_HUNT_API_KEY not set. Using test data only.")
        
        self.engine = engine
        self.session_factory = get_session
    
    async def fetch_posts(self, days_lookback: int = DEFAULT_DAYS_LOOKBACK, 
                          topic_filters: List[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch posts from Product Hunt API.
        
        Args:
            days_lookback: Number of days to look back for posts
            topic_filters: List of topic filters to apply
            
        Returns:
            List of posts data
        """
        if not self.api_key:
            logger.info("Using test data (no API key)")
            return self._get_test_data()
        
        # Set default topic filters if none provided
        if topic_filters is None:
            topic_filters = DEFAULT_TOPIC_FILTERS
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_lookback)
        
        # GraphQL query for Product Hunt API
        query = """
        query ($after: String, $postedAfter: DateTime, $topics: [String!]) {
          posts(
            first: 50
            after: $after
            postedAfter: $postedAfter
            topics: $topics
          ) {
            edges {
              node {
                id
                name
                tagline
                description
                url
                commentsCount
                votesCount
                featuredAt
                createdAt
                topics {
                  edges {
                    node {
                      name
                    }
                  }
                }
                makers {
                  totalCount
                  edges {
                    node {
                      name
                      username
                    }
                  }
                }
                hunter {
                  name
                  username
                }
                ranks {
                  daily {
                    position
                  }
                }
              }
              cursor
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
        """
        
        variables = {
            "postedAfter": start_date.isoformat(),
            "topics": topic_filters,
            "after": None
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        all_posts = []
        has_next_page = True
        
        try:
            async with httpx.AsyncClient() as client:
                while has_next_page:
                    response = await client.post(
                        API_BASE_URL,
                        json={"query": query, "variables": variables},
                        headers=headers
                    )
                    
                    if response.status_code != 200:
                        logger.error(f"API request failed: {response.status_code} - {response.text}")
                        break
                    
                    data = response.json()
                    posts_data = data.get("data", {}).get("posts", {})
                    edges = posts_data.get("edges", [])
                    
                    for edge in edges:
                        all_posts.append(edge["node"])
                    
                    page_info = posts_data.get("pageInfo", {})
                    has_next_page = page_info.get("hasNextPage", False)
                    if has_next_page:
                        variables["after"] = page_info.get("endCursor")
        
        except Exception as e:
            logger.error(f"Error fetching posts from Product Hunt: {str(e)}")
            return self._get_test_data()
        
        logger.info(f"Fetched {len(all_posts)} posts from Product Hunt")
        return all_posts
    
    def _get_test_data(self) -> List[Dict[str, Any]]:
        """
        Get test data when API key is not available.
        
        Returns:
            List of test posts data
        """
        return [
            {
                "id": "ph_test_1",
                "name": "AI Code Assistant Pro",
                "tagline": "Write better code faster with AI",
                "description": "An AI code assistant that helps developers write better code faster.",
                "url": "https://www.producthunt.com/posts/ai-code-assistant-pro",
                "commentsCount": 42,
                "votesCount": 876,
                "featuredAt": "2024-04-15T08:00:00Z",
                "createdAt": "2024-04-15T06:30:00Z",
                "topics": {
                    "edges": [
                        {"node": {"name": "Artificial Intelligence"}},
                        {"node": {"name": "Developer Tools"}},
                        {"node": {"name": "Productivity"}}
                    ]
                },
                "makers": {
                    "totalCount": 2,
                    "edges": [
                        {"node": {"name": "Jane Smith", "username": "janesmith"}},
                        {"node": {"name": "Mike Johnson", "username": "mikej"}}
                    ]
                },
                "hunter": {
                    "name": "Product Hunter",
                    "username": "producthunter"
                },
                "ranks": {
                    "daily": {
                        "position": 1
                    }
                }
            },
            {
                "id": "ph_test_2",
                "name": "DataViz Pro",
                "tagline": "Create beautiful data visualizations in seconds",
                "description": "A tool that helps you create beautiful data visualizations without coding.",
                "url": "https://www.producthunt.com/posts/dataviz-pro",
                "commentsCount": 28,
                "votesCount": 532,
                "featuredAt": "2024-04-10T08:00:00Z",
                "createdAt": "2024-04-10T07:15:00Z",
                "topics": {
                    "edges": [
                        {"node": {"name": "Productivity"}},
                        {"node": {"name": "SaaS"}},
                        {"node": {"name": "Analytics"}}
                    ]
                },
                "makers": {
                    "totalCount": 3,
                    "edges": [
                        {"node": {"name": "John Doe", "username": "johndoe"}},
                        {"node": {"name": "Sarah Parker", "username": "sarahp"}},
                        {"node": {"name": "Alex Kim", "username": "alexk"}}
                    ]
                },
                "hunter": {
                    "name": "Tech Hunter",
                    "username": "techhunter"
                },
                "ranks": {
                    "daily": {
                        "position": 3
                    }
                }
            }
        ]
    
    async def _convert_post_to_entity(self, post: Dict[str, Any]) -> ProductLaunchEvent:
        """
        Convert a Product Hunt post to a ProductLaunchEvent entity.
        
        Args:
            post: Post data from Product Hunt API
            
        Returns:
            ProductLaunchEvent entity
        """
        # Extract topics
        topics = []
        for edge in post.get("topics", {}).get("edges", []):
            topics.append(edge["node"]["name"])
        
        # Parse dates
        featured_at = post.get("featuredAt")
        launch_date = datetime.fromisoformat(featured_at.replace("Z", "+00:00")) if featured_at else None
        if not launch_date:
            created_at = post.get("createdAt")
            launch_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if created_at else datetime.now()
        
        # Get ranking
        daily_rank = None
        if post.get("ranks", {}).get("daily", {}).get("position"):
            daily_rank = post.get("ranks", {}).get("daily", {}).get("position")
        
        entity = ProductLaunchEvent(
            id=f"ph_{post.get('id')}",
            source_id=post.get("id"),
            name=post.get("name"),
            product_name=post.get("name"),
            launch_date=launch_date,
            upvotes=post.get("votesCount", 0),
            comments_count=post.get("commentsCount", 0),
            maker_count=post.get("makers", {}).get("totalCount", 0),
            topics=topics,
            tagline=post.get("tagline", ""),
            description=post.get("description", ""),
            hunter_name=post.get("hunter", {}).get("name", ""),
            url=post.get("url", ""),
            ranking=daily_rank,
            featured=featured_at is not None
        )
        
        return entity
    
    async def _find_company_by_name(self, product_name: str) -> Optional[Company]:
        """
        Find a company by name in the database.
        
        This uses a simple matching strategy. In a production environment,
        you would want to use a more sophisticated entity resolution approach.
        
        Args:
            product_name: Name of the product
            
        Returns:
            Company entity if found, None otherwise
        """
        with self.session_factory() as session:
            # Try to find company with exact name match
            company = session.query(Company).filter(Company.name == product_name).first()
            
            if not company:
                # Try to find company where product name contains company name or vice versa
                companies = session.query(Company).all()
                for c in companies:
                    if c.name.lower() in product_name.lower() or product_name.lower() in c.name.lower():
                        return c
            
            return company
    
    async def ingest(self, days_lookback: int = DEFAULT_DAYS_LOOKBACK,
                     topic_filters: List[str] = None) -> Tuple[int, int]:
        """
        Ingest product launch data from Product Hunt.
        
        Args:
            days_lookback: Number of days to look back for posts
            topic_filters: List of topic filters to apply
            
        Returns:
            Tuple of (num_entities_created, num_relationships_created)
        """
        logger.info("Starting Product Hunt ingestion")
        
        # Fetch posts from Product Hunt
        posts = await self.fetch_posts(days_lookback, topic_filters)
        
        num_entities = 0
        num_relationships = 0
        
        if not posts:
            logger.warning("No posts found from Product Hunt")
            return num_entities, num_relationships
        
        with self.session_factory() as session:
            for post in posts:
                try:
                    # Convert post to entity
                    entity = await self._convert_post_to_entity(post)
                    
                    # Check if entity already exists
                    existing = session.query(ProductLaunchEvent).filter(
                        ProductLaunchEvent.source_id == entity.source_id
                    ).first()
                    
                    if not existing:
                        # Create entity
                        session.add(entity)
                        num_entities += 1
                        logger.info(f"Created product launch entity: {entity.name}")
                        
                        # Try to find associated company
                        company = await self._find_company_by_name(entity.product_name)
                        
                        if company:
                            # Create relationship between company and product launch
                            relationship = ProductLaunchRelationship(
                                id=f"ph_rel_{uuid.uuid4()}",
                                from_entity_id=company.id,
                                to_entity_id=entity.id,
                                launch_date=entity.launch_date,
                                upvotes=entity.upvotes,
                                properties={
                                    "featured": entity.featured,
                                    "daily_ranking": entity.ranking
                                }
                            )
                            
                            session.add(relationship)
                            num_relationships += 1
                            logger.info(f"Created product launch relationship for company: {company.name}")
                    
                except Exception as e:
                    logger.error(f"Error processing post {post.get('id')}: {str(e)}")
            
            session.commit()
        
        logger.info(f"Product Hunt ingestion completed. Created {num_entities} entities and {num_relationships} relationships")
        return num_entities, num_relationships