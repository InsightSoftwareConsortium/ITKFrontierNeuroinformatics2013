/*=========================================================================
 *
 *  Copyright Insight Software Consortium
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0.txt
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *
 *=========================================================================*/

#include "itkBinaryDilateImageFilter.h"
#include "itkBinaryOpeningByReconstructionImageFilter.h"
#include "itkFlatStructuringElement.h"
#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"
#include "itkMaskImageFilter.h"
#include "itkThresholdImageFilter.h"

#include "itkStripTsImageFilter.h"

int main( int argc, char * argv[] )
{
  if( argc < 6 )
    {
    std::cerr << "Usage: "
              << argv[0]
              << " patientImageFile atlasImageFile atlasMaskFile"
              << " outputMaskFile outputPatientMaskFile"
              << std::endl;
    return EXIT_FAILURE;
    }
  const char * patientImageFilename = argv[1];
  const char * atlasImageFilename = argv[2];
  const char * atlasMaskFilename = argv[3];
  const char * outputMaskFilename = argv[4];
  const char * outputPatientMaskFile = argv[5];

  const unsigned int Dimension = 3;
  typedef float                                       PixelType;
  typedef itk::Image< PixelType, Dimension >          PatientImageType;
  typedef short                                       AtlasPixelType;
  typedef itk::Image< AtlasPixelType, Dimension >     AtlasImageType;
  typedef unsigned char                               AtlasMaskPixelType;
  typedef itk::Image< AtlasMaskPixelType, Dimension > AtlasMaskImageType;

  typedef itk::ImageFileReader< PatientImageType > PatientReaderType;
  PatientReaderType::Pointer patientReader = PatientReaderType::New();
  patientReader->SetFileName( patientImageFilename );

  typedef itk::ImageFileReader< AtlasImageType > AtlasReaderType;
  AtlasReaderType::Pointer atlasReader = AtlasReaderType::New();
  atlasReader->SetFileName( atlasImageFilename );

  typedef itk::ImageFileReader< AtlasMaskImageType > AtlasMaskReaderType;
  AtlasMaskReaderType::Pointer atlasMaskReader = AtlasMaskReaderType::New();
  atlasMaskReader->SetFileName( atlasMaskFilename );

  try
    {
    patientReader->Update();
    atlasReader->Update();
    atlasMaskReader->Update();
    }
  catch( itk::ExceptionObject & error )
    {
    std::cerr << "Error: " << error << std::endl;
    return EXIT_FAILURE;
    }

  typedef itk::StripTsImageFilter< PatientImageType, AtlasImageType, AtlasMaskImageType > StripTsFilterType;
  StripTsFilterType::Pointer stripTsFilter = StripTsFilterType::New();
  stripTsFilter->SetInput( patientReader->GetOutput() );
  stripTsFilter->SetAtlasImage( atlasReader->GetOutput() );
  stripTsFilter->SetAtlasBrainMask( atlasMaskReader->GetOutput() );

  typedef itk::FlatStructuringElement< Dimension > StructuringElementType;

  typedef itk::BinaryDilateImageFilter< AtlasMaskImageType, AtlasMaskImageType, StructuringElementType > DilateFilterType;
  DilateFilterType::Pointer dilateFilter = DilateFilterType::New();
  dilateFilter->SetInput( stripTsFilter->GetOutput() );
  dilateFilter->SetDilateValue( 1 );
  StructuringElementType::RadiusType bigRadius;
  bigRadius.Fill( 6 );
  StructuringElementType bigDilateStructuringElement = StructuringElementType::Ball( bigRadius );
  dilateFilter->SetKernel( bigDilateStructuringElement );

  typedef itk::MaskImageFilter< PatientImageType, AtlasMaskImageType, PatientImageType > PatientMaskFilterType;
  PatientMaskFilterType::Pointer oversegmentMaskedFilter = PatientMaskFilterType::New();
  oversegmentMaskedFilter->SetInput1( patientReader->GetOutput() );
  oversegmentMaskedFilter->SetInput2( dilateFilter->GetOutput() );

  typedef itk::BinaryThresholdImageFilter< PatientImageType, AtlasMaskImageType > ThresholdFilterType;
  ThresholdFilterType::Pointer thresholdFilter = ThresholdFilterType::New();
  thresholdFilter->SetUpperThreshold( 3000000 );
  thresholdFilter->SetInsideValue( 0 );
  thresholdFilter->SetOutsideValue( 1 );
  thresholdFilter->SetInput( oversegmentMaskedFilter->GetOutput() );

  typedef itk::BinaryOpeningByReconstructionImageFilter< AtlasMaskImageType, StructuringElementType > ReconstructionFilterType;
  ReconstructionFilterType::Pointer reconstructionFilter = ReconstructionFilterType::New();
  reconstructionFilter->SetRadius( 10 );
  reconstructionFilter->SetBackgroundValue( 0 );
  reconstructionFilter->SetForegroundValue( 1 );
  reconstructionFilter->SetInput( thresholdFilter->GetOutput() );

  DilateFilterType::Pointer smallDilateFilter = DilateFilterType::New();
  smallDilateFilter->SetDilateValue( 1 );
  StructuringElementType::RadiusType smallRadius;
  smallRadius.Fill( 2 );
  StructuringElementType smallDilateStructuringElement = StructuringElementType::Ball( smallRadius );
  smallDilateFilter->SetKernel( smallDilateStructuringElement );
  smallDilateFilter->SetInput( reconstructionFilter->GetOutput() );

  AtlasMaskImageType::Pointer patientMask = smallDilateFilter->GetOutput();

  PatientMaskFilterType::Pointer patientMaskFilter = PatientMaskFilterType::New();
  patientMaskFilter->SetInput1( patientReader->GetOutput() );
  patientMaskFilter->SetInput2( patientMask );

  typedef itk::ImageFileWriter< AtlasMaskImageType > MaskWriterType;
  MaskWriterType::Pointer maskWriter = MaskWriterType::New();
  maskWriter->SetFileName( outputMaskFilename );
  maskWriter->SetInput( patientMask );

  typedef itk::ImageFileWriter< PatientImageType > MaskedPatientWriterType;
  MaskedPatientWriterType::Pointer maskedPatientWriter = MaskedPatientWriterType::New();
  maskedPatientWriter->SetFileName( outputPatientMaskFile );
  maskedPatientWriter->SetInput( patientMaskFilter->GetOutput() );
  try
    {
    maskWriter->Update();
    maskedPatientWriter->Update();
    }
  catch( itk::ExceptionObject & error )
    {
    std::cerr << "Error: " << error << std::endl;
    return EXIT_FAILURE;
    }

  return EXIT_SUCCESS;
};
