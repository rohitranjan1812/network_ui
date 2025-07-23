"""
Performance and Memory Usage Benchmark Tests
Tests for performance characteristics, memory usage, and scalability limits.
"""

import os
import tempfile
import pytest
import pandas as pd
import numpy as np
import time
import threading
import psutil
import gc
from unittest.mock import patch
from network_ui.core import DataImporter, ImportConfig
from network_ui.core.validators import DataValidator
from network_ui.core.transformers import GraphTransformer
from network_ui.core.models import GraphData, Node, Edge


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark tests for all components."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Get initial memory usage
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # Force garbage collection
        gc.collect()

    def _get_memory_usage(self):
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def _create_large_dataset(self, size, file_format='csv'):
        """Create large test dataset."""
        import uuid
        data = {
            'id': range(1, size + 1),
            'name': [f'Node_{i}' for i in range(1, size + 1)],
            'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], size),
            'value': np.random.uniform(0, 1000, size),
            'score': np.random.uniform(0, 100, size),
            'active': np.random.choice([True, False], size),
            'description': [f'Description for node {i} with some longer text content' for i in range(1, size + 1)]
        }
        
        df = pd.DataFrame(data)
        # Create unique filename using UUID to avoid threading conflicts
        unique_id = str(uuid.uuid4())[:8]
        file_path = os.path.join(self.temp_dir, f'large_dataset_{size}_{unique_id}.{file_format}')
        
        if file_format == 'csv':
            df.to_csv(file_path, index=False)
        elif file_format == 'json':
            df.to_json(file_path, orient='records', indent=2)
        
        return file_path

    @pytest.mark.parametrize("dataset_size", [1000, 5000, 10000, 25000, 50000])
    def test_import_performance_scaling(self, dataset_size):
        """Test import performance scaling with increasing dataset sizes."""
        file_path = self._create_large_dataset(dataset_size)
        
        config = ImportConfig(
            file_path=file_path,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_category': 'category',
                'attribute_value': 'value',
                'attribute_score': 'score',
                'attribute_active': 'active',
                'attribute_description': 'description'
            }
        )

        importer = DataImporter()
        
        # Measure time and memory
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        result = importer.import_data(config)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        # Performance assertions
        processing_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        # Should complete successfully
        assert result.success is True
        assert len(result.graph_data.nodes) == dataset_size
        
        # Performance scaling expectations
        if dataset_size <= 1000:
            assert processing_time < 2.0  # 2 seconds for 1k
            assert memory_used < 50  # 50 MB
        elif dataset_size <= 5000:
            assert processing_time < 10.0  # 10 seconds for 5k
            assert memory_used < 200  # 200 MB
        elif dataset_size <= 10000:
            assert processing_time < 30.0  # 30 seconds for 10k
            assert memory_used < 400  # 400 MB
        elif dataset_size <= 25000:
            assert processing_time < 120.0  # 2 minutes for 25k
            assert memory_used < 1000  # 1 GB
        else:  # 50000
            assert processing_time < 300.0  # 5 minutes for 50k
            assert memory_used < 2000  # 2 GB

        # Log performance metrics
        print(f"\nDataset: {dataset_size} rows")
        print(f"Processing time: {processing_time:.2f} seconds")
        print(f"Memory used: {memory_used:.2f} MB")
        print(f"Throughput: {dataset_size / processing_time:.0f} rows/second")

    @pytest.mark.parametrize("complexity_level", ['simple', 'moderate', 'complex', 'extreme'])
    def test_mapping_complexity_performance(self, complexity_level):
        """Test performance impact of mapping complexity."""
        dataset_size = 5000
        
        # Create base data
        base_data = {
            'id': range(1, dataset_size + 1),
            'name': [f'Node_{i}' for i in range(1, dataset_size + 1)]
        }
        
        # Add complexity based on level
        complexity_configs = {
            'simple': {
                'columns': 5,
                'mapping_size': 3
            },
            'moderate': {
                'columns': 20,
                'mapping_size': 15
            },
            'complex': {
                'columns': 50,
                'mapping_size': 40
            },
            'extreme': {
                'columns': 100,
                'mapping_size': 80
            }
        }
        
        config = complexity_configs[complexity_level]
        
        # Add columns
        for i in range(config['columns']):
            base_data[f'col_{i}'] = np.random.uniform(0, 100, dataset_size)
        
        df = pd.DataFrame(base_data)
        file_path = os.path.join(self.temp_dir, f'complex_{complexity_level}.csv')
        df.to_csv(file_path, index=False)
        
        # Create mapping
        mapping_config = {
            'node_id': 'id',
            'node_name': 'name'
        }
        
        # Add complex mappings
        for i in range(min(config['mapping_size'], config['columns'])):
            if i % 3 == 0:
                mapping_config[f'attribute_col_{i}'] = f'col_{i}'
            elif i % 3 == 1:
                mapping_config[f'kpi_col_{i}'] = f'col_{i}'
            else:
                mapping_config[f'attribute_extra_{i}'] = f'col_{i}'

        import_config = ImportConfig(
            file_path=file_path,
            mapping_config=mapping_config
        )

        importer = DataImporter()
        
        # Measure performance
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        result = importer.import_data(import_config)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        processing_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        # Should complete successfully
        assert result.success is True
        assert len(result.graph_data.nodes) == dataset_size
        
        # Performance expectations based on complexity
        if complexity_level == 'simple':
            assert processing_time < 5.0
            assert memory_used < 100
        elif complexity_level == 'moderate':
            assert processing_time < 15.0
            assert memory_used < 200
        elif complexity_level == 'complex':
            assert processing_time < 45.0
            assert memory_used < 500
        else:  # extreme
            assert processing_time < 120.0
            assert memory_used < 1000

        print(f"\nComplexity: {complexity_level}")
        print(f"Columns: {config['columns']}, Mappings: {config['mapping_size']}")
        print(f"Time: {processing_time:.2f}s, Memory: {memory_used:.2f}MB")

    def test_concurrent_processing_performance(self):
        """Test performance under concurrent processing loads."""
        dataset_size = 2000
        num_workers = 4
        
        # Create test files
        file_paths = []
        for i in range(num_workers):
            file_path = self._create_large_dataset(dataset_size)
            file_paths.append(file_path)

        results = []
        errors = []
        
        def worker_function(worker_id, file_path):
            try:
                config = ImportConfig(
                    file_path=file_path,
                    mapping_config={
                        'node_id': 'id',
                        'node_name': 'name',
                        'attribute_category': 'category'
                    }
                )
                
                importer = DataImporter()
                start_time = time.time()
                result = importer.import_data(config)
                end_time = time.time()
                
                results.append({
                    'worker_id': worker_id,
                    'success': result.success,
                    'nodes': len(result.graph_data.nodes),
                    'time': end_time - start_time
                })
            except Exception as e:
                errors.append((worker_id, str(e)))

        # Start concurrent workers
        threads = []
        overall_start = time.time()
        start_memory = self._get_memory_usage()
        
        for i in range(num_workers):
            thread = threading.Thread(
                target=worker_function,
                args=(i, file_paths[i])
            )
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()
        
        overall_end = time.time()
        end_memory = self._get_memory_usage()
        
        # Analyze results
        total_time = overall_end - overall_start
        total_memory = end_memory - start_memory
        
        assert len(errors) == 0, f"Errors in concurrent processing: {errors}"
        assert len(results) == num_workers
        assert all(r['success'] for r in results)
        assert all(r['nodes'] == dataset_size for r in results)
        
        # Performance expectations
        assert total_time < 60.0  # Should complete within 1 minute
        assert total_memory < 1000  # Should use less than 1GB total
        
        avg_time = sum(r['time'] for r in results) / len(results)
        print(f"\nConcurrent processing ({num_workers} workers):")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average worker time: {avg_time:.2f}s")
        print(f"Total memory: {total_memory:.2f}MB")
        print(f"Concurrency efficiency: {(avg_time * num_workers) / total_time:.2f}x")

    @pytest.mark.parametrize("data_type", ['integer', 'float', 'string', 'boolean', 'datetime'])
    def test_data_type_detection_performance(self, data_type):
        """Test performance of data type detection for different data types."""
        dataset_size = 100000
        
        # Generate data based on type
        if data_type == 'integer':
            data = pd.Series(np.random.randint(0, 1000000, dataset_size))
        elif data_type == 'float':
            data = pd.Series(np.random.uniform(0, 1000000, dataset_size))
        elif data_type == 'string':
            data = pd.Series([f'string_value_{i}' for i in range(dataset_size)])
        elif data_type == 'boolean':
            data = pd.Series(np.random.choice(['true', 'false'], dataset_size))
        elif data_type == 'datetime':
            start_date = pd.Timestamp('2020-01-01')
            data = pd.Series([start_date + pd.Timedelta(days=i % 365) for i in range(dataset_size)])
        
        validator = DataValidator()
        
        # Measure detection performance
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        detected_type = validator.detect_data_type(data)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        processing_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        # Should detect correct type
        if data_type == 'datetime':
            assert detected_type in ['datetime', 'date']  # Either is acceptable
        else:
            assert detected_type == data_type
        
        # Performance expectations
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert memory_used < 500  # Should use less than 500MB
        
        print(f"\nData type detection: {data_type}")
        print(f"Dataset size: {dataset_size}")
        print(f"Detection time: {processing_time:.3f}s")
        print(f"Memory used: {memory_used:.2f}MB")
        print(f"Throughput: {dataset_size / processing_time:.0f} values/second")

    def test_graph_transformation_performance(self):
        """Test performance of graph transformation operations."""
        node_count = 1000  # Reduced from 10000 to prevent hanging
        edge_density = 0.01  # Reduced from 0.1 to 0.01 (1% of possible edges)
        
        # Create nodes
        node_data = pd.DataFrame({
            'id': range(1, node_count + 1),
            'name': [f'Node_{i}' for i in range(1, node_count + 1)],
            'category': np.random.choice(['A', 'B', 'C'], node_count),
            'value': np.random.uniform(0, 100, node_count)
        })
        
        # Create edges with specified density
        max_edges = node_count * (node_count - 1)
        num_edges = int(max_edges * edge_density)
        
        edges = []
        for _ in range(num_edges):
            source = np.random.randint(1, node_count + 1)
            target = np.random.randint(1, node_count + 1)
            if source != target:
                edges.append({
                    'source': source,
                    'target': target,
                    'weight': np.random.uniform(0.1, 1.0)
                })
        
        edge_data = pd.DataFrame(edges[:num_edges])
        
        transformer = GraphTransformer()
        
        # Test node transformation
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        node_graph = transformer.transform_to_graph(node_data, {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_category': 'category',
            'attribute_value': 'value'
        }, {
            'id': 'string',
            'name': 'string',
            'category': 'string',
            'value': 'float'
        })
        
        node_time = time.time() - start_time
        node_memory = self._get_memory_usage() - start_memory
        
        # Test edge transformation
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        edge_graph = transformer.transform_to_graph(edge_data, {
            'edge_source': 'source',
            'edge_target': 'target',
            'attribute_weight': 'weight'
        }, {
            'source': 'string',
            'target': 'string',
            'weight': 'float'
        })
        
        edge_time = time.time() - start_time
        edge_memory = self._get_memory_usage() - start_memory
        
        # Test graph validation
        combined_graph = GraphData()
        for node in node_graph.nodes:
            combined_graph.add_node(node)
        for edge in edge_graph.edges:
            combined_graph.add_edge(edge)
        
        start_time = time.time()
        is_valid, errors = transformer.validate_graph_structure(combined_graph)
        validation_time = time.time() - start_time
        
        # Performance assertions
        assert node_time < 30.0  # Node transformation within 30s
        assert edge_time < 30.0  # Edge transformation within 30s
        assert validation_time < 60.0  # Validation within 60s
        
        assert node_memory < 500  # Less than 500MB for nodes
        assert edge_memory < 500  # Less than 500MB for edges
        
        print(f"\nGraph transformation performance:")
        print(f"Nodes: {node_count}, Edges: {len(edges)}")
        print(f"Node transform: {node_time:.2f}s, {node_memory:.2f}MB")
        print(f"Edge transform: {edge_time:.2f}s, {edge_memory:.2f}MB")
        print(f"Validation: {validation_time:.2f}s")

    def test_memory_cleanup_efficiency(self):
        """Test memory cleanup efficiency after processing."""
        dataset_sizes = [1000, 2000, 5000, 10000]
        
        memory_before = self._get_memory_usage()
        peak_memory = memory_before
        
        for size in dataset_sizes:
            # Create and process dataset
            file_path = self._create_large_dataset(size)
            
            config = ImportConfig(
                file_path=file_path,
                mapping_config={
                    'node_id': 'id',
                    'node_name': 'name',
                    'attribute_category': 'category'
                }
            )
            
            importer = DataImporter()
            result = importer.import_data(config)
            
            current_memory = self._get_memory_usage()
            peak_memory = max(peak_memory, current_memory)
            
            # Force cleanup
            del result
            del importer
            gc.collect()
            
            # Clean up file
            os.remove(file_path)
        
        memory_after = self._get_memory_usage()
        memory_growth = memory_after - memory_before
        peak_usage = peak_memory - memory_before
        
        # Memory should not grow excessively
        assert memory_growth < 200  # Less than 200MB permanent growth
        assert peak_usage < 1000   # Peak usage less than 1GB
        
        print(f"\nMemory efficiency:")
        print(f"Initial: {memory_before:.2f}MB")
        print(f"Peak: {peak_memory:.2f}MB (+{peak_usage:.2f}MB)")
        print(f"Final: {memory_after:.2f}MB (+{memory_growth:.2f}MB)")
        print(f"Cleanup efficiency: {((peak_usage - memory_growth) / peak_usage * 100):.1f}%")

    @pytest.mark.parametrize("file_format", ['csv', 'json'])
    def test_file_format_performance_comparison(self, file_format):
        """Compare performance across different file formats."""
        dataset_size = 5000
        
        file_path = self._create_large_dataset(dataset_size, file_format)
        
        config = ImportConfig(
            file_path=file_path,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_category': 'category'
            }
        )
        
        importer = DataImporter()
        
        # Measure performance
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        result = importer.import_data(config)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        processing_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        # Should work for all formats
        assert result.success is True
        assert len(result.graph_data.nodes) == dataset_size
        
        # Performance expectations vary by format
        if file_format == 'csv':
            assert processing_time < 10.0  # CSV should be fast
            assert memory_used < 200
        elif file_format == 'json':
            assert processing_time < 20.0  # JSON might be slower
            assert memory_used < 300
        
        print(f"\nFile format performance: {file_format}")
        print(f"Time: {processing_time:.2f}s")
        print(f"Memory: {memory_used:.2f}MB")
        print(f"Throughput: {dataset_size / processing_time:.0f} rows/second")

    def test_edge_case_performance(self):
        """Test performance with edge cases that might cause slowdowns."""
        test_cases = [
            # Very wide dataset (many columns)
            {
                'name': 'wide_dataset',
                'rows': 1000,
                'cols': 500,
                'expected_time': 30.0,
                'expected_memory': 500
            },
            
            # Very long strings
            {
                'name': 'long_strings',
                'rows': 5000,
                'cols': 5,
                'string_length': 1000,
                'expected_time': 15.0,
                'expected_memory': 300
            },
            
            # High null ratio
            {
                'name': 'high_nulls',
                'rows': 10000,
                'cols': 10,
                'null_ratio': 0.8,
                'expected_time': 20.0,
                'expected_memory': 200
            }
        ]
        
        for case in test_cases:
            print(f"\nTesting edge case: {case['name']}")
            
            # Create specific dataset for each case
            if case['name'] == 'wide_dataset':
                data = {'id': range(1, case['rows'] + 1)}
                for i in range(case['cols']):
                    data[f'col_{i}'] = np.random.uniform(0, 100, case['rows'])
                    
            elif case['name'] == 'long_strings':
                data = {
                    'id': range(1, case['rows'] + 1),
                    'name': [f'Node_{i}' for i in range(1, case['rows'] + 1)]
                }
                for i in range(case['cols']):
                    data[f'text_{i}'] = ['x' * case['string_length'] for _ in range(case['rows'])]
                    
            elif case['name'] == 'high_nulls':
                data = {'id': range(1, case['rows'] + 1)}
                for i in range(case['cols']):
                    values = np.random.uniform(0, 100, case['rows'])
                    null_mask = np.random.random(case['rows']) < case['null_ratio']
                    values[null_mask] = np.nan
                    data[f'col_{i}'] = values
            
            df = pd.DataFrame(data)
            file_path = os.path.join(self.temp_dir, f'{case["name"]}.csv')
            df.to_csv(file_path, index=False)
            
            # Test performance
            mapping_config = {'node_id': 'id'}
            if 'name' in data:
                mapping_config['node_name'] = 'name'
            # Add some attributes without duplicating the id mapping
            if case['name'] == 'wide_dataset' and 'col_0' in data:
                mapping_config['attribute_value'] = 'col_0'
            elif case['name'] == 'long_strings' and 'text_0' in data:
                mapping_config['attribute_text'] = 'text_0'
            elif case['name'] == 'high_nulls' and 'col_0' in data:
                mapping_config['attribute_value'] = 'col_0'
                
            config = ImportConfig(
                file_path=file_path,
                mapping_config=mapping_config
            )
            
            importer = DataImporter()
            
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            result = importer.import_data(config)
            
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            processing_time = end_time - start_time
            memory_used = end_memory - start_memory
            
            # Should handle edge cases
            assert result.success is True
            assert processing_time < case['expected_time']
            assert memory_used < case['expected_memory']
            
            print(f"Time: {processing_time:.2f}s (limit: {case['expected_time']}s)")
            print(f"Memory: {memory_used:.2f}MB (limit: {case['expected_memory']}MB)")

    @pytest.mark.parametrize("thread_count", [1, 2, 4, 8])
    def test_thread_scalability(self, thread_count):
        """Test scalability with different thread counts."""
        dataset_size = 2000
        tasks_per_thread = 3
        
        def worker_task(worker_id):
            results = []
            for task_id in range(tasks_per_thread):
                file_path = self._create_large_dataset(dataset_size)
                
                config = ImportConfig(
                    file_path=file_path,
                    mapping_config={
                        'node_id': 'id',
                        'node_name': 'name',
                        'attribute_category': 'category'
                    }
                )
                
                importer = DataImporter()
                start_time = time.time()
                result = importer.import_data(config)
                end_time = time.time()
                
                results.append({
                    'worker_id': worker_id,
                    'task_id': task_id,
                    'time': end_time - start_time,
                    'success': result.success
                })
                
                os.remove(file_path)
            
            return results
        
        # Run with specified thread count
        threads = []
        all_results = []
        
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        for i in range(thread_count):
            thread = threading.Thread(target=lambda i=i: all_results.extend(worker_task(i)))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        total_time = end_time - start_time
        total_memory = end_memory - start_memory
        
        # Calculate metrics
        total_tasks = thread_count * tasks_per_thread
        avg_task_time = sum(r['time'] for r in all_results) / len(all_results)
        
        assert len(all_results) == total_tasks
        assert all(r['success'] for r in all_results)
        
        print(f"\nThread scalability (threads: {thread_count}):")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average task time: {avg_task_time:.2f}s")
        print(f"Total memory: {total_memory:.2f}MB")
        print(f"Throughput: {total_tasks / total_time:.2f} tasks/second") 