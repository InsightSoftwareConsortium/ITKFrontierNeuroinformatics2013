#include "itkImageFileReader.h"
#include "itkExtractImageFilter.h"

template< typename TImage >
void
Register( TImage * fixed, TImage * moving )
{
}

int main( int argc, char * argv[] )
{
  if( argc < 3 )
    {
    std::cerr << "Usage: "
              << argv[0]
              << " fixedImage movingImage [--slice-only]"
              << std::endl;
    return EXIT_FAILURE;
    }
  const char * fixedImageFile = argv[1];
  const char * movingImageFile = argv[2];
  bool sliceOnly = true; // TODO: false
  if( argc > 3 )
    {
    sliceOnly = true;
    }

  typedef float PixelType;

  if( sliceOnly )
    {
    const unsigned int Dimension = 2;
    typedef itk::Image< PixelType, Dimension > ImageType;
    typedef itk::Image< PixelType, 3 >         VolumeImageType;

    typedef itk::ImageFileReader< VolumeImageType > ReaderType;
    ReaderType::Pointer fixedReader = ReaderType::New();
    fixedReader->SetFileName( fixedImageFile );
    VolumeImageType::Pointer fixedImage = fixedReader->GetOutput();
    ReaderType::Pointer movingReader = ReaderType::New();
    movingReader->SetFileName( movingImageFile );
    VolumeImageType::Pointer movingImage = movingReader->GetOutput();

    typedef itk::ExtractImageFilter< VolumeImageType, ImageType > ExtractFilterType;
    ExtractFilterType::Pointer fixedExtractor = ExtractFilterType::New();
    fixedExtractor->SetDirectionCollapseToIdentity();
    fixedExtractor->SetInput( fixedImage );
    ExtractFilterType::Pointer movingExtractor = ExtractFilterType::New();
    movingExtractor->SetDirectionCollapseToIdentity();
    movingExtractor->SetInput( movingImage );

    try
      {
      fixedReader->UpdateOutputInformation();
      movingReader->UpdateOutputInformation();

      typedef VolumeImageType::RegionType RegionType;
      typedef VolumeImageType::SizeType   SizeType;
      typedef VolumeImageType::IndexType  IndexType;

      RegionType fixedExtractionRegion = fixedImage->GetLargestPossibleRegion();
      SizeType fixedSize = fixedExtractionRegion.GetSize();
      IndexType fixedIndex = fixedExtractionRegion.GetIndex();
      fixedIndex[2] = fixedIndex[2] + fixedSize[2] / 2;
      fixedSize[2] = 0;
      fixedExtractionRegion.SetIndex( fixedIndex );
      fixedExtractionRegion.SetSize( fixedSize );

      RegionType movingExtractionRegion = movingImage->GetLargestPossibleRegion();
      SizeType movingSize = movingExtractionRegion.GetSize();
      IndexType movingIndex = movingExtractionRegion.GetIndex();
      movingIndex[2] = movingIndex[2] + movingSize[2] / 2;
      movingSize[2] = 0;
      movingExtractionRegion.SetIndex( movingIndex );
      movingExtractionRegion.SetSize( movingSize );

      fixedExtractor->SetExtractionRegion( fixedExtractionRegion );
      fixedExtractor->Update();

      movingExtractor->SetExtractionRegion( movingExtractionRegion );
      movingExtractor->Update();

      Register< ImageType >( fixedExtractor->GetOutput(), movingExtractor->GetOutput() );

      }
    catch( itk::ExceptionObject & error )
      {
      std::cerr << "Error: " << error << std::endl;
      return EXIT_FAILURE;
      }
    }
  else
    {
    const unsigned int Dimension = 2;
    //Register< ImageType >( fixed, moving );
    }

  return EXIT_SUCCESS;
};
