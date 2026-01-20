from django.core.management.base import BaseCommand
from shop.models import Category, FlowerType, Product, Banner
from decimal import Decimal


class Command(BaseCommand):
    help = 'Load sample data for the flower shop'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')
        
        # Create Categories
        categories_data = [
            {'name': 'Wedding Flowers', 'slug': 'wedding-flowers', 'occasion': 'marriage', 
             'description': 'Beautiful arrangements for your special day'},
            {'name': 'Birthday Bouquets', 'slug': 'birthday-bouquets', 'occasion': 'birthday',
             'description': 'Celebrate with colorful birthday flowers'},
            {'name': 'Anniversary Flowers', 'slug': 'anniversary-flowers', 'occasion': 'anniversary',
             'description': 'Express your love with romantic arrangements'},
            {'name': 'Valentine Special', 'slug': 'valentine-special', 'occasion': 'valentine',
             'description': 'Red roses and romantic bouquets'},
            {'name': 'Sympathy Flowers', 'slug': 'sympathy-flowers', 'occasion': 'sympathy',
             'description': 'Thoughtful arrangements for difficult times'},
            {'name': 'Get Well Soon', 'slug': 'get-well-soon', 'occasion': 'get_well',
             'description': 'Brighten someone\'s day with cheerful flowers'},
            {'name': 'Congratulations', 'slug': 'congratulations', 'occasion': 'congratulations',
             'description': 'Celebrate achievements with beautiful blooms'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['occasion']] = cat
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  Category: {cat.name} - {status}')
        
        # Create Flower Types
        flower_types_data = [
            {'name': 'Roses', 'slug': 'roses', 'description': 'Classic and romantic'},
            {'name': 'Lilies', 'slug': 'lilies', 'description': 'Elegant and fragrant'},
            {'name': 'Tulips', 'slug': 'tulips', 'description': 'Spring favorites'},
            {'name': 'Carnations', 'slug': 'carnations', 'description': 'Long-lasting beauty'},
            {'name': 'Orchids', 'slug': 'orchids', 'description': 'Exotic and sophisticated'},
            {'name': 'Sunflowers', 'slug': 'sunflowers', 'description': 'Bright and cheerful'},
            {'name': 'Gerberas', 'slug': 'gerberas', 'description': 'Colorful and vibrant'},
            {'name': 'Mixed Flowers', 'slug': 'mixed-flowers', 'description': 'Beautiful combinations'},
        ]
        
        flower_types = {}
        for ft_data in flower_types_data:
            ft, created = FlowerType.objects.get_or_create(
                slug=ft_data['slug'],
                defaults=ft_data
            )
            flower_types[ft_data['slug']] = ft
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  Flower Type: {ft.name} - {status}')
        
        # Create Products
        products_data = [
            # Wedding Flowers
            {
                'name': 'Bridal Rose Bouquet',
                'slug': 'bridal-rose-bouquet',
                'category': 'marriage',
                'price': Decimal('2999.00'),
                'discount_price': Decimal('2499.00'),
                'description': 'A stunning bridal bouquet featuring premium white and blush roses, perfect for your wedding day. Hand-tied with satin ribbon.',
                'short_description': 'Premium white & blush roses for brides',
                'flower_types': ['roses'],
                'stock': 50,
                'is_featured': True,
                'is_bestseller': True,
                'care_instructions': 'Keep in water, away from direct sunlight. Mist petals lightly.',
            },
            {
                'name': 'Wedding Lily Arrangement',
                'slug': 'wedding-lily-arrangement',
                'category': 'marriage',
                'price': Decimal('3499.00'),
                'description': 'Elegant white Oriental lilies arranged beautifully for wedding ceremonies and receptions.',
                'short_description': 'Elegant white lilies for weddings',
                'flower_types': ['lilies'],
                'stock': 30,
                'is_featured': True,
            },
            
            # Birthday Flowers
            {
                'name': 'Rainbow Birthday Bouquet',
                'slug': 'rainbow-birthday-bouquet',
                'category': 'birthday',
                'price': Decimal('1299.00'),
                'discount_price': Decimal('999.00'),
                'description': 'A vibrant mix of colorful gerberas, carnations, and chrysanthemums to make their birthday special!',
                'short_description': 'Colorful mix for birthday celebrations',
                'flower_types': ['gerberas', 'carnations', 'mixed-flowers'],
                'stock': 100,
                'is_bestseller': True,
                'is_new_arrival': True,
            },
            {
                'name': 'Sunflower Sunshine',
                'slug': 'sunflower-sunshine',
                'category': 'birthday',
                'price': Decimal('1499.00'),
                'description': 'Bright sunflowers arranged with greenery to bring sunshine to any birthday celebration.',
                'short_description': 'Bright sunflowers for happy birthdays',
                'flower_types': ['sunflowers'],
                'stock': 60,
                'is_featured': True,
            },
            
            # Anniversary Flowers
            {
                'name': 'Red Rose Romance',
                'slug': 'red-rose-romance',
                'category': 'anniversary',
                'price': Decimal('1999.00'),
                'discount_price': Decimal('1799.00'),
                'description': 'Express your love with 24 premium red roses, elegantly arranged with baby\'s breath and greenery.',
                'short_description': '24 premium red roses for your love',
                'flower_types': ['roses'],
                'stock': 80,
                'is_featured': True,
                'is_bestseller': True,
            },
            {
                'name': 'Golden Anniversary Orchids',
                'slug': 'golden-anniversary-orchids',
                'category': 'anniversary',
                'price': Decimal('2499.00'),
                'description': 'Luxurious yellow and gold orchids in an elegant vase, perfect for golden anniversary celebrations.',
                'short_description': 'Luxurious orchids for special anniversaries',
                'flower_types': ['orchids'],
                'stock': 25,
                'is_featured': True,
            },
            
            # Valentine Special
            {
                'name': 'Classic Valentine Dozen',
                'slug': 'classic-valentine-dozen',
                'category': 'valentine',
                'price': Decimal('1599.00'),
                'discount_price': Decimal('1399.00'),
                'description': 'The classic gift of love - 12 long-stemmed red roses wrapped in elegant packaging with a heart-shaped card.',
                'short_description': '12 red roses - the classic love gift',
                'flower_types': ['roses'],
                'stock': 150,
                'is_bestseller': True,
            },
            {
                'name': 'Valentine Heart Box',
                'slug': 'valentine-heart-box',
                'category': 'valentine',
                'price': Decimal('2299.00'),
                'description': 'Red roses arranged in a beautiful heart-shaped box with chocolates. The perfect Valentine\'s surprise!',
                'short_description': 'Roses in heart box with chocolates',
                'flower_types': ['roses'],
                'stock': 75,
                'is_featured': True,
                'is_new_arrival': True,
            },
            
            # Get Well Soon
            {
                'name': 'Cheerful Get Well Basket',
                'slug': 'cheerful-get-well-basket',
                'category': 'get_well',
                'price': Decimal('1199.00'),
                'description': 'A cheerful arrangement of yellow and orange flowers to brighten their recovery. Includes gerberas, roses, and carnations.',
                'short_description': 'Bright flowers to speed up recovery',
                'flower_types': ['gerberas', 'roses', 'carnations'],
                'stock': 40,
            },
            
            # Congratulations
            {
                'name': 'Victory Celebration Bouquet',
                'slug': 'victory-celebration-bouquet',
                'category': 'congratulations',
                'price': Decimal('1799.00'),
                'description': 'Celebrate their success with this magnificent arrangement of lilies, roses, and exotic flowers.',
                'short_description': 'Grand bouquet for big achievements',
                'flower_types': ['lilies', 'roses', 'mixed-flowers'],
                'stock': 35,
                'is_featured': True,
            },
            
            # Sympathy
            {
                'name': 'Peaceful Lily Wreath',
                'slug': 'peaceful-lily-wreath',
                'category': 'sympathy',
                'price': Decimal('2999.00'),
                'description': 'A serene wreath of white lilies and roses, expressing sympathy and peace during difficult times.',
                'short_description': 'Serene white arrangement for condolences',
                'flower_types': ['lilies', 'roses'],
                'stock': 20,
            },
        ]
        
        for prod_data in products_data:
            flower_type_slugs = prod_data.pop('flower_types')
            category_key = prod_data.pop('category')
            prod_data['category'] = categories[category_key]
            
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults=prod_data
            )
            
            if created:
                for ft_slug in flower_type_slugs:
                    if ft_slug in flower_types:
                        product.flower_types.add(flower_types[ft_slug])
            
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  Product: {product.name} - {status}')
        
        # Create Banners
        banners_data = [
            {
                'title': 'Wedding Season Sale',
                'subtitle': 'Up to 30% off on wedding flowers',
                'button_text': 'Shop Wedding',
                'button_link': '/products/?occasion=marriage',
                'position': 1,
            },
            {
                'title': 'Fresh Roses Daily',
                'subtitle': 'Farm-fresh roses delivered to your doorstep',
                'button_text': 'Order Now',
                'button_link': '/products/',
                'position': 2,
            },
        ]
        
        for banner_data in banners_data:
            banner, created = Banner.objects.get_or_create(
                title=banner_data['title'],
                defaults=banner_data
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  Banner: {banner.title} - {status}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data loaded successfully!'))
        self.stdout.write('\nSummary:')
        self.stdout.write(f'  Categories: {Category.objects.count()}')
        self.stdout.write(f'  Flower Types: {FlowerType.objects.count()}')
        self.stdout.write(f'  Products: {Product.objects.count()}')
        self.stdout.write(f'  Banners: {Banner.objects.count()}')
