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

#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"
#include "itkMaskImageFilter.h"

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

  typedef itk::MaskImageFilter< PatientImageType, AtlasMaskImageType, PatientImageType > PatientMaskFilterType;
  PatientMaskFilterType::Pointer patientMaskFilter = PatientMaskFilterType::New();
  patientMaskFilter->SetInput1( patientReader->GetOutput() );
  patientMaskFilter->SetInput2( stripTsFilter->GetOutput() );

  typedef itk::ImageFileWriter< AtlasMaskImageType > MaskWriterType;
  MaskWriterType::Pointer maskWriter = MaskWriterType::New();
  maskWriter->SetFileName( outputMaskFilename );
  maskWriter->SetInput( stripTsFilter->GetOutput() );

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
