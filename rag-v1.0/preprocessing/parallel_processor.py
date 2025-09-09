"""
Parallel PDF Batch Processor
Uses the existing working batch_pdf_processor function in parallel.
"""

import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from batch_pdf_processor import process_all_pdfs


def split_pdf_list(pdf_files, num_chunks):
    """Split PDF list into chunks for parallel processing."""
    chunk_size = len(pdf_files) // num_chunks
    chunks = []
    
    for i in range(num_chunks):
        start = i * chunk_size
        if i == num_chunks - 1:  # Last chunk gets remaining files
            end = len(pdf_files)
        else:
            end = start + chunk_size
        
        if start < len(pdf_files):
            chunks.append(pdf_files[start:end])
    
    return chunks


def process_pdf_batch(pdf_batch, batch_id, input_path, output_path):
    """Process a batch of PDFs using the existing function."""
    print(f"Batch {batch_id}: Processing {len(pdf_batch)} PDFs")
    
    # Create temporary input directory with just this batch
    temp_input = os.path.join(input_path, f"temp_batch_{batch_id}")
    os.makedirs(temp_input, exist_ok=True)
    
    try:
        # Copy PDFs to temp directory (symlinks for speed)
        for pdf_file in pdf_batch:
            src = os.path.join(input_path, pdf_file)
            dst = os.path.join(temp_input, pdf_file)
            if os.path.exists(src):
                # Create symlink or copy
                try:
                    os.symlink(src, dst)
                except:
                    import shutil
                    shutil.copy2(src, dst)
        
        # Use existing function on this batch
        temp_output = os.path.join(output_path, f"batch_{batch_id}")
        process_all_pdfs(input_path=temp_input, output_path=temp_output)
        
        # Move results to main output directory
        if os.path.exists(temp_output):
            for file in os.listdir(temp_output):
                src = os.path.join(temp_output, file)
                dst = os.path.join(output_path, file)
                if not os.path.exists(dst):
                    os.rename(src, dst)
            
            # Cleanup batch directory properly
            import shutil
            shutil.rmtree(temp_output)
        
        return len(pdf_batch)
        
    finally:
        # Cleanup temp directory
        import shutil
        if os.path.exists(temp_input):
            shutil.rmtree(temp_input)


def process_all_pdfs_parallel(input_path=None, output_path=None, num_workers=4):
    """Process PDFs in parallel using existing working function."""
    
    # Setup paths
    if input_path is None:
        input_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "arxiv_downloads")
    
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_chunks")
    
    os.makedirs(output_path, exist_ok=True)
    
    # Get all PDFs
    pdf_files = [f for f in os.listdir(input_path) if f.endswith('.pdf')]
    print(f"🚀 Processing {len(pdf_files)} PDFs with {num_workers} parallel batches")
    
    # Split into batches
    pdf_batches = split_pdf_list(pdf_files, num_workers)
    
    # Process batches in parallel
    total_processed = 0
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Submit all batches
        future_to_batch = {
            executor.submit(process_pdf_batch, batch, i+1, input_path, output_path): i+1 
            for i, batch in enumerate(pdf_batches)
        }
        
        # Collect results
        for future in as_completed(future_to_batch):
            batch_id = future_to_batch[future]
            try:
                processed_count = future.result()
                total_processed += processed_count
                print(f"✅ Batch {batch_id} completed: {processed_count} PDFs")
            except Exception as e:
                print(f"❌ Batch {batch_id} failed: {e}")
    
    print(f"\n🎉 Parallel processing complete!")
    print(f"Total PDFs processed: {total_processed}")
    print(f"Output directory: {output_path}")


if __name__ == "__main__":
    process_all_pdfs_parallel(num_workers=4)  # Use 4 parallel processes
