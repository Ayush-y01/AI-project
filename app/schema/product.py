from pydantic import BaseModel, Field,AnyUrl,field_validator,model_validator,computed_field,EmailStr
from typing import Annotated, Literal,Optional,List
from uuid import UUID 
from datetime import datetime

# this is for create pydantic -------------------

class DimensionsCM(BaseModel):
    length: Annotated[float, Field(gt=0, strict=True, description="Length in CM")]
    width: Annotated[float, Field(gt=0, strict=True, description="width in CM")]
    height: Annotated[float, Field(gt=0, strict=True, description="height in CM")]
    
    
    
class Seller(BaseModel):
    id:UUID
    name:Annotated[
        str,
        Field(
            min_length=2,
            max_length=60,
            title="Seller Name",
            description="Name of the seller (2-60 char)",
            examples=["Hero"]
        )
    ]
    email: EmailStr
    website: AnyUrl
    
    @field_validator("email", mode="after")
    @classmethod
    def Seller_email_validate_domain(cls,value:EmailStr):
        allowed_domain = ["mistore.in","hpworld.in","apple.com"]
        
        domain = str(value).split('@')[-1].lower()
        if domain not in allowed_domain:
            raise ValueError(f"Seller email domain not allowed: {domain}")

        return value
    


class Product(BaseModel):
    id:UUID 
    sku:Annotated[str,Field(min_length=6, max_length=30, title="SKU", description="Stock Keeping Unit", examples=["XIAO-359GB-001"])]
    name:Annotated[
        str,
        Field(
            min_length=3,
            max_length=80,
            title="Product Name",
            description="Readable Product name (3-80 char)",
            examples=["Xiaomi Model Pro"]
        )
    ]
    description: Annotated[
        str,
        Field(
            max_length=200,
            description="Short Product description"
        )
    ]
    category: Annotated[
        str,
        Field(
            min_length=3,
            max_length=30,
            description="Category of product",
            examples=["mobiles","Laptops"]
        )
    ]
    brand: Annotated[
        str,
        Field(
            min_length=2,
            max_length=40,
            examples=["Xiaomi","Apple"]
        )
    ]
    price: Annotated[
        float,
        Field(
            gt=0,
            strict=True,
            description="Base Price(INR)"
        )
    ]
    currency: Literal["INR"] = "INR"
    
    discount_percent: Annotated[
        int,
        Field(
            ge=0,
            le=90,
            description="Discount percent"
        ),
    ] = 0
    
    stock: Annotated[
        int,
        Field(
            ge=0,
            description="Available Stock"
        )
    ]
    is_active: Annotated[
        bool,
        Field(
            description="Is Product Active?"
        )
    ]
    rating: Annotated[
        float,
        Field(ge=0, le=5, strict=True, description="Rating out of 5")
    ]
    tags: Annotated[
        Optional[List[str]],
        Field(default=None,max_length=10, description="up to 10 Tags")
    ]
    image_urls: Annotated[
        Optional[AnyUrl],
        Field(min_length=1, description="Atleast 1 Image is require")
    ]
    
    dimensions_cm : DimensionsCM
    seller: Seller
    created_at: datetime
    
    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_formate(cls,value:str):
        if "-"not in value:
            raise ValueError("Sku must have '-' ")
        
        last = value.split('-')[-1]
        
        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("sku must end with 3 digit sequence -234")
        
        
        return value 
    
    @model_validator(mode="after")
    @classmethod
    def validate_buisness_rules(cls, model: "Product"):
        if model.stock == 0 and model.is_active is True:
            raise ValueError("If stock is 0, is_active must be false")
        
        if model.discount_percent > 0 and model.rating == 0:
            raise ValueError("disocunted price must have a rating")
        
        return model
    
    @computed_field
    @property
    def final_price(self) -> float:
        return round(self.price * (1 - self.discount_percent / 100), 2)
    
    @computed_field
    @property
    def volume_cm3(self) -> float:
        d = self.dimensions_cm
        
        return round(d.length * d.width * d.height, 2)
    
    

# this is for update pydantic -------------------


class DimensionsCMUpdate(BaseModel):
    length: Optional[float] = Field(gt=0)
    width: Optional[float] = Field(gt=0)
    height: Optional[float] = Field(gt=0)
    
    
    
class SellerUpdate(BaseModel):
    name: Optional[str] = Field(min_length=2, max_length=60)
    email: Optional[EmailStr] 
    website: Optional[AnyUrl]
    
    @field_validator("email", mode="after")
    @classmethod
    def Seller_email_validate_domain(cls,value:EmailStr):
        allowed_domain = ["mistore.in","hpworld.in","apple.com"]
        
        domain = str(value).split('@')[-1].lower()
        if domain not in allowed_domain:
            raise ValueError(f"Seller email domain not allowed: {domain}")

        return value

class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(min_length=6, max_length=30)

    name: Optional[str] = Field(min_length=3, max_length=60)
    description: Optional[str] = Field(max_length=200)
    category: Optional[str]
    brand: Optional[str]

    price: Optional[float] = Field(gt=0)
    currency: Optional[Literal["INR"]]

    discount_percent: Optional[int] = Field(ge=0, le=90)

    stock: Optional[int] = Field(ge=0)
    is_active: Optional[bool]
    rating: Optional[float] = Field(ge=0, le=5)

    tags: Optional[List[str]] = Field(max_length=10)
    image_urls: Optional[List[AnyUrl]]

    dimensions_cm: Optional[DimensionsCMUpdate]
    seller: Optional[SellerUpdate]
    created_at: Optional[datetime]
    
    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_formate(cls, value: Optional[str]):
        if value is None:
            return value

        if "-" not in value:
            raise ValueError("Sku must have '-' ")

        last = value.split('-')[-1]

        if not (len(last) == 3 and last.isdigit()):
            raise ValueError("sku must end with 3 digit sequence -234")

        return value
    
    @model_validator(mode="after")
    @classmethod
    def validate_buisness_rules(cls, model: "ProductUpdate"):
        if model.stock == 0 and model.is_active is True:
            raise ValueError("If stock is 0, is_active must be false")
        
        if model.discount_percent > 0 and model.rating == 0:
            raise ValueError("disocunted price must have a rating")
        
        return model
    
    @computed_field
    @property
    def final_price(self) -> Optional[float]:
        if self.price is None:
            return None

        discount = self.discount_percent or 0
        return round(self.price * (1 - discount / 100), 2)

    @computed_field
    @property
    def volume_cm3(self) -> float:
        d = self.dimensions_cm
        
        return round(d.length * d.width * d.height, 2)